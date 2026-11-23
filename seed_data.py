"""Seed AroundU with a realistic demo dataset.

Usage:
    flask --app app seed          # only seeds when the database is empty
    flask --app app seed --drop   # wipes and reseeds
"""

from datetime import date, timedelta

from constants import ROLE_ORGANIZER, ROLE_STUDENT, STATUS_ACCEPTED, STATUS_PENDING
from extensions import db
from models import Event, Registration, User

DEMO_PASSWORD = "password123"

ORGANIZERS = [
    {
        "username": "iitm_shaastra",
        "email": "events@iitm.ac.in",
        "college": "IIT Madras",
    },
    {
        "username": "anna_kurukshetra",
        "email": "events@annauniv.edu",
        "college": "Anna University, Chennai",
    },
    {
        "username": "nitt_pragyan",
        "email": "events@nitt.edu",
        "college": "NIT Trichy",
    },
    {
        "username": "psg_events",
        "email": "events@psgtech.ac.in",
        "college": "PSG College of Technology",
    },
    {
        "username": "kct_yugam",
        "email": "events@kct.ac.in",
        "college": "Kumaraguru College of Technology",
    },
    {
        "username": "gce_salem",
        "email": "events@gcesalem.edu.in",
        "college": "Government College of Engineering, Salem",
    },
    {
        "username": "loyola_events",
        "email": "events@loyolacollege.edu",
        "college": "Loyola College, Chennai",
    },
    {
        "username": "sastra_daksh",
        "email": "events@sastra.edu",
        "college": "SASTRA University",
    },
]

STUDENTS = [
    {
        "username": "student_demo",
        "email": "student@demo.com",
        "college": "Government College of Engineering, Salem",
    },
    {
        "username": "priya_r",
        "email": "priya@example.com",
        "college": "PSG College of Technology",
    },
    {
        "username": "arjun_k",
        "email": "arjun@example.com",
        "college": "IIT Madras",
    },
    {
        "username": "meena_s",
        "email": "meena@example.com",
        "college": "Loyola College, Chennai",
    },
]

EVENTS = [
    {
        "title": "Shaastra 2026",
        "description": (
            "Shaastra is the annual technical festival of IIT Madras and the first "
            "student-run ISO 9001:2015 certified festival in the world. Expect "
            "hackathons, robotics arenas, research showcases and talks from industry "
            "leaders across four days."
        ),
        "days": 34,
        "start_time": "09:00",
        "location": "IIT Madras Campus, Chennai",
        "host_college": "IIT Madras",
        "category": "Technical",
        "capacity": 500,
        "organizer": "iitm_shaastra",
        "image_url": "https://images.unsplash.com/photo-1522071820081-009f0129c71c?auto=format&fit=crop&w=1200&q=80",
    },
    {
        "title": "Kurukshetra 2026",
        "description": (
            "The international techno-management fest of Anna University. A week of "
            "competitive programming, product design challenges and a startup expo "
            "where students from every tier of college compete on the same stage."
        ),
        "days": 45,
        "start_time": "10:00",
        "location": "Anna University, Guindy, Chennai",
        "host_college": "Anna University, Chennai",
        "category": "Hackathon",
        "capacity": 300,
        "organizer": "anna_kurukshetra",
        "image_url": "https://images.unsplash.com/photo-1517245386807-bb43f82c33c4?auto=format&fit=crop&w=1200&q=80",
    },
    {
        "title": "Pragyan 2026",
        "description": (
            "Pragyan is the international techno-managerial fest of NIT Trichy. "
            "Workshops, case competitions and a 36-hour hackathon open to students "
            "from any college in India."
        ),
        "days": 60,
        "start_time": "09:30",
        "location": "NIT Trichy Campus, Tiruchirappalli",
        "host_college": "NIT Trichy",
        "category": "Technical",
        "capacity": 400,
        "organizer": "nitt_pragyan",
        "image_url": "https://images.unsplash.com/photo-1540575467063-178a50c2df87?auto=format&fit=crop&w=1200&q=80",
    },
    {
        "title": "Yugam 2026",
        "description": (
            "South India's largest techno-cultural fest hosted by Kumaraguru College "
            "of Technology. Music, dance, street theatre and a makers' fair all in "
            "one weekend."
        ),
        "days": 21,
        "start_time": "11:00",
        "location": "KCT Campus, Coimbatore",
        "host_college": "Kumaraguru College of Technology",
        "category": "Cultural",
        "capacity": 1000,
        "organizer": "kct_yugam",
        "image_url": "https://images.unsplash.com/photo-1492684223066-81342ee5ff30?auto=format&fit=crop&w=1200&q=80",
    },
    {
        "title": "Daksh 2026",
        "description": (
            "The national level technical festival of SASTRA University. Build "
            "hardware, ship software and pitch to a panel of founders."
        ),
        "days": 28,
        "start_time": "10:00",
        "location": "SASTRA University, Thanjavur",
        "host_college": "SASTRA University",
        "category": "Technical",
        "capacity": 250,
        "organizer": "sastra_daksh",
        "image_url": "https://images.unsplash.com/photo-1517048676732-d65bc937f952?auto=format&fit=crop&w=1200&q=80",
    },
    {
        "title": "PSG Tech Invente",
        "description": (
            "A hands-on workshop series on embedded systems, IoT and applied AI. "
            "Bring a laptop; every session ends with something you can demo."
        ),
        "days": 14,
        "start_time": "14:00",
        "location": "PSG College of Technology, Coimbatore",
        "host_college": "PSG College of Technology",
        "category": "Workshop",
        "capacity": 80,
        "organizer": "psg_events",
        "image_url": "https://images.unsplash.com/photo-1531482615713-2afd69097998?auto=format&fit=crop&w=1200&q=80",
    },
    {
        "title": "Salem Code Sprint",
        "description": (
            "A beginner-friendly coding sprint hosted by Government College of "
            "Engineering, Salem. Teams of three solve real problems from local "
            "businesses, with mentors on the floor all day."
        ),
        "days": 10,
        "start_time": "09:00",
        "location": "GCE Salem, Salem",
        "host_college": "Government College of Engineering, Salem",
        "category": "Hackathon",
        "capacity": 120,
        "organizer": "gce_salem",
        "image_url": "https://images.unsplash.com/photo-1519389950473-47ba0277781c?auto=format&fit=crop&w=1200&q=80",
    },
    {
        "title": "Loyola Cultural Carnival",
        "description": (
            "An open cultural carnival at Loyola College with inter-college dance, "
            "music and quiz competitions. All colleges welcome."
        ),
        "days": 17,
        "start_time": "16:00",
        "location": "Loyola College, Chennai",
        "host_college": "Loyola College, Chennai",
        "category": "Cultural",
        "capacity": 600,
        "organizer": "loyola_events",
        "image_url": "https://images.unsplash.com/photo-1470229722913-7c0e2dbbafd3?auto=format&fit=crop&w=1200&q=80",
    },
    {
        "title": "Inter-College Sports Meet",
        "description": (
            "Track and field, basketball and badminton across two days. Open to "
            "every affiliated college, with separate men's and women's draws."
        ),
        "days": 38,
        "start_time": "07:30",
        "location": "PSG Tech Grounds, Coimbatore",
        "host_college": "PSG College of Technology",
        "category": "Sports",
        "capacity": 200,
        "organizer": "psg_events",
        "image_url": "https://images.unsplash.com/photo-1461896836934-ffe607ba8211?auto=format&fit=crop&w=1200&q=80",
    },
]


def seed_database(app, drop: bool = False) -> bool:
    """Populate demo data. Returns True when new data was written."""
    with app.app_context():
        if drop:
            db.drop_all()
        db.create_all()

        if User.query.first() is not None:
            return False

        organizers = {}
        for entry in ORGANIZERS:
            user = User(
                username=entry["username"],
                email=entry["email"],
                role=ROLE_ORGANIZER,
                college_name=entry["college"],
            )
            user.set_password(DEMO_PASSWORD)
            db.session.add(user)
            organizers[entry["username"]] = user

        students = {}
        for entry in STUDENTS:
            user = User(
                username=entry["username"],
                email=entry["email"],
                role=ROLE_STUDENT,
                college_name=entry["college"],
            )
            user.set_password(DEMO_PASSWORD)
            db.session.add(user)
            students[entry["username"]] = user

        db.session.flush()

        events = []
        for entry in EVENTS:
            event = Event(
                title=entry["title"],
                description=entry["description"],
                date=date.today() + timedelta(days=entry["days"]),
                start_time=entry["start_time"],
                location=entry["location"],
                host_college=entry["host_college"],
                category=entry["category"],
                image_url=entry["image_url"],
                capacity=entry["capacity"],
                organizer_id=organizers[entry["organizer"]].id,
            )
            db.session.add(event)
            events.append(event)

        db.session.flush()

        demo_student = students["student_demo"]
        db.session.add(
            Registration(
                user_id=demo_student.id,
                event_id=events[0].id,
                status=STATUS_ACCEPTED,
            )
        )
        db.session.add(
            Registration(
                user_id=students["priya_r"].id,
                event_id=events[0].id,
                status=STATUS_PENDING,
            )
        )
        db.session.add(
            Registration(
                user_id=students["arjun_k"].id,
                event_id=events[3].id,
                status=STATUS_PENDING,
            )
        )

        db.session.commit()
        return True


if __name__ == "__main__":
    from app import app as flask_app

    seed_database(flask_app, drop=True)
    print("Database seeded.")
