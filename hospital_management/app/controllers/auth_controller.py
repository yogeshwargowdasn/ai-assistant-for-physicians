from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from app.models.user import User
from app import db
from urllib.parse import urlparse, urljoin

auth_bp = Blueprint('auth', __name__)

# Helper function to validate redirect URLs
def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc

@auth_bp.route('/')
def index():
    return redirect(url_for('auth.login'))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('auth.dashboard'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user, remember=True)
            next_page = request.args.get('next')
            if next_page and is_safe_url(next_page):
                return redirect(next_page)
            return redirect(url_for('auth.dashboard'))
        
        flash("Invalid credentials", "danger")

    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('auth.dashboard'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Username already exists", "warning")
            return redirect(url_for('auth.register'))

        hashed_pw = generate_password_hash(password)
        new_user = User(username=username, password=hashed_pw, role=role)
        db.session.add(new_user)
        db.session.commit()
        flash("Account created successfully. Please log in.", "success")
        return redirect(url_for("auth.login"))


    return render_template('register.html')

@auth_bp.route('/dashboard')
@login_required
def dashboard():
    # Optional: role-based access control
    # if current_user.role != 'admin':
    #     flash("Access denied: Admins only", "danger")
    #     return redirect(url_for('auth.login'))
    return render_template('dashboard.html', user=current_user)

@auth_bp.route('/logout')
@login_required
def logout():
    user_id = str(current_user.id)
    if 'submitted_symptoms' in session and isinstance(session['submitted_symptoms'], dict):
        session['submitted_symptoms'].pop(user_id, None)

    logout_user()
    flash('Logout successful', 'info')
    return redirect(url_for('auth.login'))


