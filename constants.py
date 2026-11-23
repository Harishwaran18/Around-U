"""Domain constants shared by models, routes, forms and seed data."""

ROLE_STUDENT = "student"
ROLE_ORGANIZER = "organizer"
ROLES = (ROLE_STUDENT, ROLE_ORGANIZER)

STATUS_PENDING = "pending"
STATUS_ACCEPTED = "accepted"
STATUS_REJECTED = "rejected"
REGISTRATION_STATUSES = (STATUS_PENDING, STATUS_ACCEPTED, STATUS_REJECTED)

EVENT_CATEGORIES = (
    "Technical",
    "Cultural",
    "Workshop",
    "Hackathon",
    "Sports",
    "Other",
)

# A starting list for the registration dropdown. Students can still type their
# own college via the "Other" option, so this is not a hard restriction.
COLLEGES = (
    "IIT Madras",
    "Anna University, Chennai",
    "NIT Trichy",
    "VIT Vellore",
    "PSG College of Technology",
    "SSN College of Engineering",
    "Kumaraguru College of Technology",
    "Thiagarajar College of Engineering",
    "Coimbatore Institute of Technology",
    "SASTRA University",
    "Loyola College, Chennai",
    "Government College of Engineering, Salem",
    "Sri Krishna College of Technology",
    "Bannari Amman Institute of Technology",
)

MAX_USERNAME_LENGTH = 80
MAX_EMAIL_LENGTH = 150
MIN_PASSWORD_LENGTH = 8
