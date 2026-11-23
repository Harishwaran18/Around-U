"""Database models for AroundU."""

from datetime import UTC, date, datetime

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from constants import ROLE_ORGANIZER, ROLE_STUDENT, STATUS_ACCEPTED, STATUS_PENDING
from extensions import db


def utcnow() -> datetime:
    """Naive UTC timestamp, stored consistently across SQLite and PostgreSQL."""
    return datetime.now(UTC).replace(tzinfo=None)


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(150), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default=ROLE_STUDENT)
    college_name = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=utcnow, nullable=False)

    events_organized = db.relationship(
        "Event",
        back_populates="organizer",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    registrations = db.relationship(
        "Registration",
        back_populates="participant",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    @property
    def is_organizer(self) -> bool:
        return self.role == ROLE_ORGANIZER

    @property
    def is_student(self) -> bool:
        return self.role == ROLE_STUDENT

    @property
    def initials(self) -> str:
        return self.username[:2].upper() if self.username else "?"

    def __repr__(self) -> str:
        return f"<User {self.username} ({self.role})>"


class Event(db.Model):
    __tablename__ = "events"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    date = db.Column(db.Date, nullable=False, index=True)
    start_time = db.Column(db.String(20), nullable=True)
    location = db.Column(db.String(255), nullable=False)
    host_college = db.Column(db.String(200), nullable=False, index=True)
    category = db.Column(db.String(60), nullable=False, index=True)
    image_url = db.Column(db.String(500), nullable=True)
    capacity = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=utcnow, nullable=False)

    organizer_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    organizer = db.relationship("User", back_populates="events_organized")
    registrations = db.relationship(
        "Registration",
        back_populates="event",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    @property
    def registration_count(self) -> int:
        return len(self.registrations)

    @property
    def accepted_count(self) -> int:
        return sum(1 for reg in self.registrations if reg.status == STATUS_ACCEPTED)

    @property
    def pending_count(self) -> int:
        return sum(1 for reg in self.registrations if reg.status == STATUS_PENDING)

    @property
    def seats_left(self):
        if self.capacity is None:
            return None
        return max(self.capacity - self.registration_count, 0)

    @property
    def is_full(self) -> bool:
        return self.capacity is not None and self.registration_count >= self.capacity

    @property
    def is_past(self) -> bool:
        return self.date < date.today()

    def __repr__(self) -> str:
        return f"<Event {self.title} @ {self.host_college}>"


class Registration(db.Model):
    __tablename__ = "registrations"
    __table_args__ = (
        db.UniqueConstraint("user_id", "event_id", name="uq_registration_user_event"),
    )

    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(20), nullable=False, default=STATUS_PENDING)
    applied_at = db.Column(db.DateTime, default=utcnow, nullable=False)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    event_id = db.Column(
        db.Integer,
        db.ForeignKey("events.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    participant = db.relationship("User", back_populates="registrations")
    event = db.relationship("Event", back_populates="registrations")

    def __repr__(self) -> str:
        return f"<Registration user={self.user_id} event={self.event_id} status={self.status}>"
