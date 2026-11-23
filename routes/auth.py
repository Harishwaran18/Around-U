"""Registration, sign-in and sign-out."""

import re

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy import func, or_

from constants import (
    COLLEGES,
    MAX_EMAIL_LENGTH,
    MAX_USERNAME_LENGTH,
    MIN_PASSWORD_LENGTH,
    ROLE_STUDENT,
    ROLES,
)
from extensions import db
from models import User

auth_bp = Blueprint("auth", __name__)

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[A-Za-z]{2,}$")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""
        role = (request.form.get("role") or ROLE_STUDENT).strip()
        college = (request.form.get("college") or "").strip()

        if college == "Other":
            college = (request.form.get("other_college") or "").strip()

        errors = []
        if not 3 <= len(username) <= MAX_USERNAME_LENGTH:
            errors.append("Username must be between 3 and 80 characters.")
        if not EMAIL_RE.match(email) or len(email) > MAX_EMAIL_LENGTH:
            errors.append("Enter a valid email address.")
        if len(password) < MIN_PASSWORD_LENGTH:
            errors.append(f"Password must be at least {MIN_PASSWORD_LENGTH} characters.")
        if role not in ROLES:
            errors.append("Choose a valid account type.")
        if not college:
            errors.append("Select or enter your college.")

        if not errors:
            existing = User.query.filter(
                or_(func.lower(User.email) == email, func.lower(User.username) == username.lower())
            ).first()
            if existing:
                errors.append("An account with that email or username already exists.")

        if errors:
            for message in errors:
                flash(message, "error")
            return (
                render_template(
                    "auth/register.html",
                    colleges=COLLEGES,
                    form={"username": username, "email": email, "role": role, "college": college},
                ),
                400,
            )

        user = User(username=username, email=email, role=role, college_name=college)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        login_user(user)
        flash(f"Welcome to AroundU, {user.username}!", "success")
        return redirect(url_for("main.dashboard"))

    return render_template(
        "auth/register.html", colleges=COLLEGES, form={"role": ROLE_STUDENT, "college": ""}
    )


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""
        remember = request.form.get("remember") == "on"

        user = User.query.filter(func.lower(User.email) == email).first()
        if user is None or not user.check_password(password):
            flash("Invalid email or password.", "error")
            return render_template("auth/login.html", form={"email": email}), 401

        login_user(user, remember=remember)
        flash(f"Welcome back, {user.username}!", "success")

        next_url = request.args.get("next")
        if next_url and next_url.startswith("/") and not next_url.startswith("//"):
            return redirect(next_url)
        return redirect(url_for("main.dashboard"))

    return render_template("auth/login.html", form={})


@auth_bp.get("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been signed out.", "info")
    return redirect(url_for("main.index"))

