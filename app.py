"""AroundU application factory.

Run locally with:
    flask --app app run --debug
Serve in production with:
    gunicorn app:app
"""

import click
from flask import Flask, render_template

from config import Config
from extensions import csrf, db, login_manager
from models import User


def create_app(config_class=Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)

    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please sign in to continue."
    login_manager.login_message_category = "info"

    @login_manager.user_loader
    def load_user(user_id: str):
        return db.session.get(User, int(user_id))

    from routes.auth import auth_bp
    from routes.events import events_bp
    from routes.main import main_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(events_bp)

    _register_error_handlers(app)
    _register_cli(app)

    if app.config["SECRET_KEY"] in ("", "dev-secret-key-change-me") and not app.debug:
        app.logger.warning(
            "SECRET_KEY is the development default. Set the SECRET_KEY "
            "environment variable before deploying."
        )

    with app.app_context():
        if app.config.get("AUTO_CREATE_TABLES", True):
            db.create_all()
        if app.config.get("SEED_ON_STARTUP"):
            from seed_data import seed_database

            seed_database(app, drop=False)

    return app


def _register_error_handlers(app: Flask) -> None:
    @app.errorhandler(403)
    def forbidden(error):
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def not_found(error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error(error):
        db.session.rollback()
        return render_template("errors/500.html"), 500


def _register_cli(app: Flask) -> None:
    @app.cli.command("init-db")
    def init_db():
        """Create any missing database tables."""
        db.create_all()
        click.echo("Database tables are ready.")

    @app.cli.command("seed")
    @click.option("--drop", is_flag=True, help="Drop existing tables before seeding.")
    def seed(drop: bool):
        """Load demo organizers, students and events."""
        from seed_data import seed_database

        created = seed_database(app, drop=drop)
        if created:
            click.echo(
                "Demo data seeded. Sign in with student@demo.com / password123 (student) "
                "or events@iitm.ac.in / password123 (organizer)."
            )
        else:
            click.echo("Database already has data. Re-run with --drop to reset.")

    @app.cli.command("create-organizer")
    @click.option("--username", prompt=True)
    @click.option("--email", prompt=True)
    @click.option("--college", prompt="College")
    @click.password_option()
    def create_organizer(username: str, email: str, college: str, password: str):
        """Create an organizer account from the command line."""
        if User.query.filter((User.email == email.lower()) | (User.username == username)).first():
            raise click.ClickException("A user with that username or email already exists.")

        user = User(
            username=username.strip(),
            email=email.strip().lower(),
            role="organizer",
            college_name=college.strip(),
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        click.echo(f"Organizer {username} created.")

    @app.shell_context_processor
    def shell_context():
        return {"db": db, "User": User}


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
