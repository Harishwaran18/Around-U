"""Shared Flask extension instances.

Kept in their own module so models, routes and the app factory can import them
without creating circular imports.
"""

from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()
