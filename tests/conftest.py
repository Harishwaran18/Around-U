"""Shared pytest fixtures for the AroundU test suite."""

from datetime import date, timedelta

import pytest

from app import create_app
from config import TestingConfig
from extensions import db as _db
from models import Event, User

PASSWORD = "password123"


@pytest.fixture()
def app():
    application = create_app(TestingConfig)
    with application.app_context():
        _db.drop_all()
        _db.create_all()
        yield application
        _db.session.remove()
        _db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def db(app):
    return _db


def _create_user(app, username, email, role, college):
    with app.app_context():
        user = User(username=username, email=email, role=role, college_name=college)
        user.set_password(PASSWORD)
        _db.session.add(user)
        _db.session.commit()
        return user.id


@pytest.fixture()
def student_id(app):
    return _create_user(app, "student1", "student1@example.com", "student", "IIT Madras")


@pytest.fixture()
def organizer_id(app):
    return _create_user(app, "organizer1", "organizer1@example.com", "organizer", "NIT Trichy")


@pytest.fixture()
def event_id(app, organizer_id):
    with app.app_context():
        event = Event(
            title="Test Hackathon",
            description="A test event for the automated suite.",
            date=date.today() + timedelta(days=10),
            start_time="09:00",
            location="Main Hall",
            host_college="NIT Trichy",
            category="Hackathon",
            capacity=2,
            organizer_id=organizer_id,
        )
        _db.session.add(event)
        _db.session.commit()
        return event.id


@pytest.fixture()
def login(client):
    def _login(email, password=PASSWORD):
        return client.post(
            "/login",
            data={"email": email, "password": password},
            follow_redirects=True,
        )

    return _login


@pytest.fixture()
def register(client):
    def _register(**overrides):
        data = {
            "username": "newstudent",
            "email": "newstudent@example.com",
            "password": PASSWORD,
            "role": "student",
            "college": "IIT Madras",
        }
        data.update(overrides)
        return client.post("/register", data=data, follow_redirects=True)

    return _register
