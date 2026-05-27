from flask import Blueprint, render_template, request, redirect, url_for, session, send_file
from extensions import db
from models import User, Request, Approval
import io
from reportlab.pdfgen import canvas

auth = Blueprint('auth', __name__)


# -------------------------
# REGISTER
# -------------------------
@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        new_user = User(
            username=username,
            password=password,
            role='user'
        )

        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('auth.login'))

    return render_template('register.html')


# -------------------------
# LOGIN
# -------------------------
@auth.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(
            username=username,
            password=password
        ).first()

        if user:
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role

            return redirect(url_for('auth.dashboard'))

        return "Invalid username or password"

    return render_template('login.html')


# -------------------------
# DASHBOARD
# -------------------------
@auth.route('/dashboard')
def dashboard():

    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    username = session.get('username')
    role = session.get('role')

    if role == 'user':
        return render_template('dashboard_user.html', username=username)

    elif role == 'isibo':
        return render_template('dashboard_isibo.html', username=username)

    elif role == 'village':
        return render_template('dashboard_village.html', username=username)

    elif role == 'sector':
        return render_template('dashboard_sector.html', username=username)

    return "Unknown role"


# -------------------------
# MY REQUESTS
# -------------------------
@auth.route('/my_requests')
def my_requests():

    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    user_id = session['user_id']

    data = Request.query.filter_by(user_id=user_id).all()

    return render_template('my_requests.html', requests=data)


# -------------------------
# CREATE REQUEST
# -------------------------
@auth.route('/request', methods=['GET', 'POST'])
def request_house():

    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    if request.method == 'POST':

        new_request = Request(
            user_id=session['user_id'],
            location=request.form['location'],
            description=request.form['description']
        )

        db.session.add(new_request)
        db.session.commit()

        return "Request submitted successfully!"

    return render_template('request_form.html')


# -------------------------
# ISIBO REQUESTS
# -------------------------
@auth.route('/isibo/requests')
def isibo_requests():

    if session.get('role') != 'isibo':
        return redirect(url_for('auth.login'))

    data = Request.query.filter_by(status='pending_isibo').all()

    return render_template('isibo_requests.html', requests=data)


@auth.route('/isibo/action/<int:request_id>/<string:action>', methods=['POST'])
def isibo_action(request_id, action):

    if session.get('role') != 'isibo':
        return redirect(url_for('auth.login'))

    req = Request.query.get(request_id)

    if req:

        req.status = 'pending_village' if action == 'approve' else 'rejected'

        approval = Approval(
            request_id=request_id,
            level='isibo',
            decision=action,
            reason=request.form['reason'],
            approved_by=session['user_id']
        )

        db.session.add(approval)
        db.session.commit()

    return redirect(url_for('auth.isibo_requests'))


# -------------------------
# VILLAGE REQUESTS
# -------------------------
@auth.route('/village/requests')
def village_requests():

    if session.get('role') != 'village':
        return redirect(url_for('auth.login'))

    data = Request.query.filter_by(status='pending_village').all()

    return render_template('village_requests.html', requests=data)


@auth.route('/village/action/<int:request_id>/<string:action>', methods=['POST'])
def village_action(request_id, action):

    if session.get('role') != 'village':
        return redirect(url_for('auth.login'))

    req = Request.query.get(request_id)

    if req:

        req.status = 'pending_sector' if action == 'approve' else 'rejected'

        approval = Approval(
            request_id=request_id,
            level='village',
            decision=action,
            reason=request.form['reason'],
            approved_by=session['user_id']
        )

        db.session.add(approval)
        db.session.commit()

    return redirect(url_for('auth.village_requests'))


# -------------------------
# SECTOR REQUESTS
# -------------------------
@auth.route('/sector/requests')
def sector_requests():

    if session.get('role') != 'sector':
        return redirect(url_for('auth.login'))

    data = Request.query.filter_by(status='pending_sector').all()

    return render_template('sector_requests.html', requests=data)


@auth.route('/sector/action/<int:request_id>/<string:action>', methods=['POST'])
def sector_action(request_id, action):

    if session.get('role') != 'sector':
        return redirect(url_for('auth.login'))

    req = Request.query.get(request_id)

    if req:

        req.status = 'approved' if action == 'approve' else 'rejected'

        approval = Approval(
            request_id=request_id,
            level='sector',
            decision=action,
            reason=request.form['reason'],
            approved_by=session['user_id']
        )

        db.session.add(approval)
        db.session.commit()

    return redirect(url_for('auth.sector_requests'))


# -------------------------
# PDF DOWNLOAD
# -------------------------
@auth.route('/download/<int:request_id>')
def download_permission(request_id):

    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    req = Request.query.get(request_id)

    if not req:
        return "Request not found"

    buffer = io.BytesIO()

    pdf = canvas.Canvas(buffer)

    pdf.setFont("Helvetica", 12)

    pdf.drawString(100, 800, "OFFICIAL HOUSE CONSTRUCTION PERMISSION")

    pdf.drawString(100, 760, f"Request ID: {req.id}")

    pdf.drawString(100, 740, f"User ID: {req.user_id}")

    pdf.drawString(100, 720, f"Location: {req.location}")

    pdf.drawString(100, 700, f"Description: {req.description}")

    pdf.drawString(100, 680, "Status: APPROVED BY SECTOR")

    pdf.save()

    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name="permission.pdf"
    )


# -------------------------
# LOGOUT
# -------------------------
@auth.route('/logout')
def logout():

    session.clear()

    return redirect(url_for('auth.login'))