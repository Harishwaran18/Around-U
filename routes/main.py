"""Public pages: landing page, dashboard and health check."""

from flask import Blueprint, jsonify, render_template, request
from flask_login import current_user, login_required
from sqlalchemy import func, or_, text

from constants import EVENT_CATEGORIES
from extensions import db
from models import Event, Registration, User

main_bp = Blueprint("main", __name__)


@main_bp.get("/")
def index():
    search = (request.args.get("q") or "").strip()
    category = (request.args.get("category") or "").strip()
    college = (request.args.get("college") or "").strip()

    query = Event.query
    if search:
        like = f"%{search.lower()}%"
        query = query.filter(
            or_(
                func.lower(Event.title).like(like),
                func.lower(Event.description).like(like),
                func.lower(Event.location).like(like),
                func.lower(Event.host_college).like(like),
                func.lower(Event.category).like(like),
            )
        )
    if category:
        query = query.filter(Event.category == category)
    if college:
        query = query.filter(Event.host_college == college)

    events = query.order_by(Event.date.asc(), Event.title.asc()).all()
    colleges = [
        row[0]
        for row in db.session.query(Event.host_college)
        .distinct()
        .order_by(Event.host_college.asc())
        .all()
    ]

    stats = {
        "events": Event.query.count(),
        "colleges": db.session.query(func.count(func.distinct(Event.host_college))).scalar() or 0,
        "students": User.query.filter_by(role="student").count(),
    }

    return render_template(
        "index.html",
        events=events,
        colleges=colleges,
        categories=EVENT_CATEGORIES,
        stats=stats,
        filters={"q": search, "category": category, "college": college},
    )


@main_bp.get("/dashboard")
@login_required
def dashboard():
    if current_user.is_organizer:
        events = (
            Event.query.filter_by(organizer_id=current_user.id)
            .order_by(Event.date.asc())
            .all()
        )
        pending = (
            db.session.query(func.count(Registration.id))
            .join(Event, Registration.event_id == Event.id)
            .filter(Event.organizer_id == current_user.id, Registration.status == "pending")
            .scalar()
            or 0
        )
        return render_template("dashboard.html", events=events, pending_count=pending)

    registrations = (
        Registration.query.filter_by(user_id=current_user.id)
        .join(Event, Registration.event_id == Event.id)
        .order_by(Event.date.asc())
        .all()
    )
    return render_template("dashboard.html", registrations=registrations)


@main_bp.get("/healthz")
def healthz():
    try:
        db.session.execute(text("SELECT 1"))
    except Exception:  # noqa: BLE001 - any DB failure means degraded
        return jsonify(status="degraded", database="error"), 503
    return jsonify(status="ok", database="ok"), 200
