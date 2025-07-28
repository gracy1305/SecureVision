from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.forms import RegistrationForm, LoginForm
from app.models import User, AuditChecklist
from app import db
from app.gpt_utils import analyze_risk


bp = Blueprint('routes', __name__)

@bp.route('/')
def home():
    return render_template('home.html')
# @bp.route('/')
# def home():
#     return render_template('home.html')
    # return "<h1>Welcome to SecureVision</h1>"

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('routes.dashboard'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Account created! You can now log in.', 'success')
        return redirect(url_for('routes.login'))
    return render_template('register.html', form=form)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('routes.dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('routes.dashboard'))
        else:
            flash('Invalid email or password.', 'danger')
    return render_template('login.html', form=form)

@bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', user=current_user)

@bp.route('/checklists')
@login_required
def checklist_index():
    checklists = AuditChecklist.query.order_by(AuditChecklist.created_at.desc()).all()
    return render_template('checklists/index.html', checklists=checklists)

@bp.route('/checklists/new', methods=['GET', 'POST'])
@login_required
def checklist_new():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        new_checklist = AuditChecklist(
            title=title,
            description=description,
            created_by=current_user.email
        )
        db.session.add(new_checklist)
        db.session.commit()
        flash('Checklist created successfully!', 'success')
        return redirect(url_for('routes.checklist_index'))
    return render_template('checklists/new.html')

@bp.route('/checklists/<int:id>/delete')
@login_required
def checklist_delete(id):
    checklist = AuditChecklist.query.get_or_404(id)
    if checklist.created_by != current_user.email:
        flash("Unauthorized!", "danger")
        return redirect(url_for('routes.checklist_index'))
    db.session.delete(checklist)
    db.session.commit()
    flash("Checklist deleted.", "info")
    return redirect(url_for('routes.checklist_index'))

@bp.route('/checklists/<int:id>/analyze')
@login_required
def analyze_checklist(id):
    checklist = AuditChecklist.query.get_or_404(id)

    if checklist.created_by != current_user.email:
        flash("You are not authorized to analyze this checklist.", "danger")
        return redirect(url_for('routes.checklist_index'))

    summary = analyze_risk(checklist.description)
    return render_template('checklists/analyze.html', checklist=checklist, summary=summary)

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You’ve been logged out.")
    return redirect(url_for('routes.login'))
