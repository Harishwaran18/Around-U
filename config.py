"""Application configuration.

Environment variables:
    SECRET_KEY            Flask session signing key (required in production).
    DATABASE_URL          SQLAlchemy database URL. Defaults to a local SQLite file.
    SESSION_COOKIE_SECURE Set to 1 when serving over HTTPS.
    AUTO_CREATE_TABLES    Set to 0 to disable automatic table creation on boot.
    SEED_ON_STARTUP       Set to 1 to seed demo data when the database is empty.
"""

import os
from pathlib import Path
from typing import ClassVar

BASE_DIR = Path(__file__).resolve().parent


def build_database_uri() -> str:
    """Return a SQLAlchemy URI, normalising the legacy Heroku postgres:// scheme."""
    url = os.environ.get("DATABASE_URL", "").strip()
    if not url:
        return f"sqlite:///{BASE_DIR / 'aroundu.db'}"
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    return url


def env_flag(name: str, default: str = "0") -> bool:
    return os.environ.get(name, default).strip().lower() in {"1", "true", "yes", "on"}


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")
    SQLALCHEMY_DATABASE_URI = build_database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS: ClassVar[dict] = {"pool_pre_ping": True}

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = env_flag("SESSION_COOKIE_SECURE")
    REMEMBER_COOKIE_HTTPONLY = True
    PERMANENT_SESSION_LIFETIME = 60 * 60 * 24 * 14

    AUTO_CREATE_TABLES = env_flag("AUTO_CREATE_TABLES", "1")
    SEED_ON_STARTUP = env_flag("SEED_ON_STARTUP")


class TestingConfig(Config):
    TESTING = True
    SECRET_KEY = "test-secret-key"
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_ENGINE_OPTIONS: ClassVar[dict] = {}
    WTF_CSRF_ENABLED = False
    AUTO_CREATE_TABLES = True
    SEED_ON_STARTUP = False
