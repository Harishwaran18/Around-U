"""Event browsing, applications and organizer management."""

from datetime import date, datetime

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy.exc import IntegrityError

from constants import (
    COLLEGES,
    EVENT_CATEGORIES,
    STATUS_ACCEPTED,
    STATUS_PENDING,
    STATUS_REJECTED,
)
from extensions import db
from models import Event, Registration

events_bp = Blueprint("events", __name__, url_prefix="/events")

ACTION_TO_STATUS = {
    "accept": STATUS_ACCEPTED,
    "reject": STATUS_REJECTED,
    "pending": STATUS_PENDING,
}


def _parse_event_form():
    """Validate the event form. Returns (data, errors)."""
    title = (request.form.get("title") or "").strip()
    description = (request.form.get("description") or "").strip()
    date_str = (request.form.get("date") or "").strip()
    start_time = (request.form.get("start_time") or "").strip()
    location = (request.form.get("location") or "").strip()
    host_college = (request.form.get("host_college") or "").strip()
    category = (request.form.get("category") or "").strip()
    image_url = (request.form.get("image_url") or "").strip()
    capacity_raw = (request.form.get("capacity") or "").strip()

    errors = []
    if not title:
        errors.append("Event title is required.")
    elif len(title) > 200:
        errors.append("Event title must be 200 characters or fewer.")
    if not description:
        errors.append("Event description is required.")
    if not location:
        errors.append("Location is required.")
    if not host_college:
        errors.append("Host college is required.")
    if category not in EVENT_CATEGORIES:
        errors.append("Choose a valid category.")
    if image_url and not image_url.startswith(("http://", "https://")):
        errors.append("Image URL must start with http:// or https://.")

    event_date = None
    try:
        event_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        errors.append("Enter a valid event date.")
    else:
        if event_date < date.today():
            errors.append("Event date cannot be in the past.")

    capacity = None
    if capacity_raw:
        try:
            capacity = int(capacity_raw)
        except ValueError:
            errors.append("Capacity must be a whole number.")
        else:
            if capacity < 1:
                errors.append("Capacity must be at least 1.")

    if errors:
        return None, errors

    return {
        "title": title,
        "description": description,
        "date": event_date,
        "start_time": start_time or None,
        "location": location,
        "host_college": host_college,
        "category": category,
        "image_url": image_url or None,
        "capacity": capacity,
    }, []


def _owned_event_or_404(event_id: int) -> Event:
    event = db.session.get(Event, event_id)
    if event is None:
        abort(404)
    if event.organizer_id != current_user.id:
        abort(403)
    return event


@events_bp.route("/create", methods=["GET", "POST"])
@login_required
def create_event():
    if not current_user.is_organizer:
        abort(403)

    if request.method == "POST":
        data, errors = _parse_event_form()
        if errors:
            for message in errors:
                flash(message, "error")
            return (
                render_template(
                    "events/create_event.html",
                    categories=EVENT_CATEGORIES,
                    colleges=COLLEGES,
                    form=request.form,
                ),
                400,
            )

        event = Event(**data, organizer_id=current_user.id)
        db.session.add(event)
        db.session.commit()
        flash("Event published successfully.", "success")
        return redirect(url_for("events.event_details", event_id=event.id))

    return render_template(
        "events/create_event.html",
        categories=EVENT_CATEGORIES,
        colleges=COLLEGES,
        form={"host_college": current_user.college_name},
    )


@events_bp.get("/<int:event_id>")
def event_details(event_id: int):
    event = db.session.get(Event, event_id)
    if event is None:
        abort(404)

    registration = None
    if current_user.is_authenticated and current_user.is_student:
        registration = Registration.query.filter_by(
            user_id=current_user.id, event_id=event.id
        ).first()

    return render_template("events/event_details.html", event=event, registration=registration)


@events_bp.post("/<int:event_id>/apply")
@login_required
def apply_event(event_id: int):
    if not current_user.is_student:
        abort(403)

    event = db.session.get(Event, event_id)
    if event is None:
        abort(404)

    existing = Registration.query.filter_by(
        user_id=current_user.id, event_id=event.id
    ).first()

    if existing:
        flash("You have already applied for this event.", "info")
    elif event.is_past:
        flash("This event has already taken place.", "error")
    elif event.is_full:
        flash("This event is full.", "error")
    else:
        db.session.add(Registration(user_id=current_user.id, event_id=event.id))
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash("You have already applied for this event.", "info")
        else:
            flash("Application submitted. The organizer will review it.", "success")

    return redirect(url_for("events.event_details", event_id=event.id))


@events_bp.post("/<int:event_id>/cancel")
@login_required
def cancel_registration(event_id: int):
    if not current_user.is_student:
        abort(403)

    registration = Registration.query.filter_by(
        user_id=current_user.id, event_id=event_id
    ).first()
    if registration is None:
        flash("You have not applied for this event.", "info")
    else:
        db.session.delete(registration)
        db.session.commit()
        flash("Your application has been withdrawn.", "success")

    return redirect(url_for("events.event_details", event_id=event_id))


@events_bp.get("/<int:event_id>/manage")
@login_required
def manage_event(event_id: int):
    event = _owned_event_or_404(event_id)
    registrations = (
        Registration.query.filter_by(event_id=event.id)
        .order_by(Registration.applied_at.asc())
        .all()
    )
    return render_template(
        "events/manage_event.html", event=event, registrations=registrations
    )


@events_bp.post("/<int:event_id>/registrations/<int:registration_id>/<action>")
@login_required
def update_registration(event_id: int, registration_id: int, action: str):
    event = _owned_event_or_404(event_id)
    if action not in ACTION_TO_STATUS:
        abort(404)

    registration = Registration.query.filter_by(
        id=registration_id, event_id=event.id
    ).first()
    if registration is None:
        abort(404)

    registration.status = ACTION_TO_STATUS[action]
    db.session.commit()
    flash(f"{registration.participant.username}'s application marked {registration.status}.", "success")
    return redirect(url_for("events.manage_event", event_id=event.id))


@events_bp.route("/<int:event_id>/edit", methods=["GET", "POST"])
@login_required
def edit_event(event_id: int):
    event = _owned_event_or_404(event_id)

    if request.method == "POST":
        data, errors = _parse_event_form()
        if errors:
            for message in errors:
                flash(message, "error")
            return (
                render_template(
                    "events/edit_event.html",
                    event=event,
                    categories=EVENT_CATEGORIES,
                    colleges=COLLEGES,
                    form=request.form,
                ),
                400,
            )

        for field, value in data.items():
            setattr(event, field, value)
        db.session.commit()
        flash("Event updated.", "success")
        return redirect(url_for("events.event_details", event_id=event.id))

    return render_template(
        "events/edit_event.html",
        event=event,
        categories=EVENT_CATEGORIES,
        colleges=COLLEGES,
        form={
            "title": event.title,
            "description": event.description,
            "date": event.date.isoformat(),
            "start_time": event.start_time or "",
            "location": event.location,
            "host_college": event.host_college,
            "category": event.category,
            "image_url": event.image_url or "",
            "capacity": event.capacity if event.capacity is not None else "",
        },
    )


@events_bp.post("/<int:event_id>/delete")
@login_required
def delete_event(event_id: int):
    event = _owned_event_or_404(event_id)
    db.session.delete(event)
    db.session.commit()
    flash("Event deleted.", "success")
    return redirect(url_for("main.dashboard"))
