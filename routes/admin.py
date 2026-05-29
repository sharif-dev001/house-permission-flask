from flask import Blueprint
from flask import render_template
from flask import request
from flask import session
from flask import redirect

from functools import wraps

from extensions import db
from models import User
from werkzeug.security import generate_password_hash


admin = Blueprint('admin', __name__)


# -------------------------
# ADMIN ACCESS CONTROL
# -------------------------
def admin_required(f):

    @wraps(f)
    def wrapper(*args, **kwargs):

        if session.get('role') != 'admin':
            return redirect('/login')

        return f(*args, **kwargs)

    return wrapper


# -------------------------
# ADMIN DASHBOARD
# -------------------------
@admin.route('/admin/dashboard')
@admin_required
def dashboard():

    return render_template('admin/dashboard.html')


# -------------------------
# VIEW ALL USERS
# -------------------------
@admin.route('/admin/users')
@admin_required
def users():

    all_users = User.query.all()

    return render_template(
        'admin/users.html',
        users=all_users
    )


# -------------------------
# CREATE USER / LEADER
# -------------------------
@admin.route('/admin/create-user', methods=['GET', 'POST'])
@admin_required
def create_user():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']
        role = request.form['role']

        # check duplicate user
        existing = User.query.filter_by(username=username).first()

        if existing:
            return "User already exists"

        new_user = User(
            username=username,
            password=generate_password_hash(password),
            role=role
        )

        db.session.add(new_user)
        db.session.commit()

        return redirect('/admin/users')

    return render_template('admin/create_user.html')