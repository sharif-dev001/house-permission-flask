from extensions import db


# -------------------------
# USERS TABLE
# -------------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(100), unique=True, nullable=False)

    password = db.Column(db.String(100), nullable=False)

    role = db.Column(db.String(50), default='user')


# -------------------------
# REQUESTS TABLE
# -------------------------
class Request(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, nullable=False)

    location = db.Column(db.String(200), nullable=False)

    description = db.Column(db.Text, nullable=False)

    status = db.Column(db.String(50), default='pending_isibo')


# -------------------------
# APPROVALS TABLE
# -------------------------
class Approval(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    request_id = db.Column(db.Integer, nullable=False)

    level = db.Column(db.String(50), nullable=False)

    decision = db.Column(db.String(50), nullable=False)

    reason = db.Column(db.Text)

    approved_by = db.Column(db.Integer, nullable=False)