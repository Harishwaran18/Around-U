"""End-to-end tests for the AroundU routes."""

from datetime import date, timedelta

from extensions import db as _db
from models import Event, Registration, User


def _event_payload(**overrides):
    data = {
        "title": "New Fest",
        "description": "A brand new campus festival.",
        "date": (date.today() + timedelta(days=5)).isoformat(),
        "start_time": "10:00",
        "location": "Main Auditorium",
        "host_college": "NIT Trichy",
        "category": "Cultural",
        "capacity": "100",
        "image_url": "",
    }
    data.update(overrides)
    return data


def test_home_page_loads(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"AroundU" in response.data


def test_health_check_reports_ok(client):
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"


def test_unknown_page_returns_404(client):
    assert client.get("/does-not-exist").status_code == 404


def test_register_creates_student_and_signs_in(client, register, app):
    response = register()
    assert response.status_code == 200
    assert b"Your activity" in response.data and b"Applications" in response.data

    with app.app_context():
        user = User.query.filter_by(email="newstudent@example.com").first()
        assert user is not None
        assert user.role == "student"
        assert user.check_password("password123")


def test_register_rejects_short_password(client, register):
    response = register(password="short")
    assert response.status_code == 400
    assert b"at least 8 characters" in response.data


def test_register_rejects_duplicate_email(client, register, student_id):
    response = register(email="student1@example.com")
    assert response.status_code == 400
    assert b"already exists" in response.data


def test_login_rejects_bad_password(client, student_id):
    response = client.post(
        "/login",
        data={"email": "student1@example.com", "password": "wrong-password"},
        follow_redirects=True,
    )
    assert response.status_code == 401
    assert b"Invalid email or password" in response.data


def test_login_succeeds(client, student_id, login):
    response = login("student1@example.com")
    assert response.status_code == 200
    assert b"Your activity" in response.data and b"Applications" in response.data


def test_organizer_can_publish_event(client, organizer_id, login, app):
    login("organizer1@example.com")
    response = client.post("/events/create", data=_event_payload(), follow_redirects=True)
    assert response.status_code == 200
    assert b"Event published successfully" in response.data

    with app.app_context():
        event = Event.query.filter_by(title="New Fest").first()
        assert event is not None
        assert event.capacity == 100
        assert event.host_college == "NIT Trichy"


def test_event_rejects_past_date(client, organizer_id, login):
    login("organizer1@example.com")
    past = (date.today() - timedelta(days=1)).isoformat()
    response = client.post(
        "/events/create", data=_event_payload(date=past), follow_redirects=True
    )
    assert response.status_code == 400
    assert b"cannot be in the past" in response.data


def test_student_cannot_publish_event(client, student_id, login):
    login("student1@example.com")
    assert client.get("/events/create").status_code == 403


def test_student_can_apply_only_once(client, student_id, event_id, login, app):
    login("student1@example.com")

    first = client.post(f"/events/{event_id}/apply", follow_redirects=True)
    assert b"Application submitted" in first.data

    second = client.post(f"/events/{event_id}/apply", follow_redirects=True)
    assert b"already applied" in second.data

    with app.app_context():
        assert Registration.query.filter_by(event_id=event_id).count() == 1


def test_capacity_is_enforced(client, student_id, event_id, login, app):
    with app.app_context():
        for index in range(2):
            filler = User(
                username=f"filler{index}",
                email=f"filler{index}@example.com",
                role="student",
                college_name="Some College",
            )
            filler.set_password("password123")
            _db.session.add(filler)
        _db.session.commit()

    login("student1@example.com")
    client.post(f"/events/{event_id}/apply", follow_redirects=True)
    client.get("/logout")

    login("filler0@example.com")
    client.post(f"/events/{event_id}/apply", follow_redirects=True)
    client.get("/logout")

    login("filler1@example.com")
    response = client.post(f"/events/{event_id}/apply", follow_redirects=True)
    assert b"event is full" in response.data.lower()


def test_organizer_can_accept_application(client, student_id, organizer_id, event_id, login, app):
    login("student1@example.com")
    client.post(f"/events/{event_id}/apply", follow_redirects=True)
    client.get("/logout")

    with app.app_context():
        registration_id = Registration.query.filter_by(event_id=event_id).first().id

    login("organizer1@example.com")
    response = client.post(
        f"/events/{event_id}/registrations/{registration_id}/accept",
        follow_redirects=True,
    )
    assert b"accepted" in response.data

    with app.app_context():
        assert _db.session.get(Registration, registration_id).status == "accepted"


def test_organizer_cannot_manage_another_organizers_event(client, app, event_id, login):
    with app.app_context():
        other = User(
            username="other_organizer",
            email="other@example.com",
            role="organizer",
            college_name="Some College",
        )
        other.set_password("password123")
        _db.session.add(other)
        _db.session.commit()

    login("other@example.com")
    assert client.get(f"/events/{event_id}/manage").status_code == 403


def test_student_can_withdraw_application(client, student_id, event_id, login, app):
    login("student1@example.com")
    client.post(f"/events/{event_id}/apply", follow_redirects=True)

    response = client.post(f"/events/{event_id}/cancel", follow_redirects=True)
    assert b"withdrawn" in response.data

    with app.app_context():
        assert Registration.query.filter_by(event_id=event_id).count() == 0


def test_search_filters_events(client, event_id):
    assert b"Test Hackathon" in client.get("/?q=Hackathon").data
    assert b"No events match" in client.get("/?q=zzzzz").data


def test_event_details_page_is_public(client, event_id):
    response = client.get(f"/events/{event_id}")
    assert response.status_code == 200
    assert b"Test Hackathon" in response.data
