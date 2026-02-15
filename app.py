import os
import uuid
from datetime import datetime
from flask import Flask, render_template, redirect, url_for, flash, request, abort, jsonify, send_file
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import json

from config import Config
from models import db, User, Course, Module, Content, Quiz, Question, Assignment
from models import Enrollment, Progress, QuizAttempt, Submission, Certificate, ForumThread, ForumPost
from forms import RegistrationForm, LoginForm, CourseForm, ModuleForm, ContentForm
from forms import QuizForm, QuestionForm, AssignmentForm

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Routes
@app.route('/')
def index():
    courses = Course.query.order_by(Course.created_at.desc()).limit(6).all()
    return render_template('index.html', courses=courses)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        user = User(
            username=form.username.data,
            email=form.email.data,
            password=hashed_password
        )
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You can now log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash('Login unsuccessful. Check email and password.', 'danger')

    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.is_instructor:
        teaching_courses = Course.query.filter_by(instructor_id=current_user.id).all()
        return render_template('dashboard.html', teaching_courses=teaching_courses)
    else:
        enrollments = Enrollment.query.filter_by(student_id=current_user.id).all()
        return render_template('dashboard.html', enrollments=enrollments)


# Course Management
@app.route('/course/create', methods=['GET', 'POST'])
@login_required
def create_course():
    if not current_user.is_instructor:
        abort(403)

    form = CourseForm()
    if form.validate_on_submit():
        thumbnail_filename = None
        if form.thumbnail.data:
            file = form.thumbnail.data
            thumbnail_filename = secure_filename(f"{uuid.uuid4()}_{file.filename}")
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], thumbnail_filename))

        course = Course(
            title=form.title.data,
            description=form.description.data,
            category=form.category.data,
            thumbnail=thumbnail_filename,
            instructor_id=current_user.id
        )
        db.session.add(course)
        db.session.commit()
        flash('Course created successfully!', 'success')
        return redirect(url_for('manage_course', course_id=course.id))

    return render_template('create_course.html', form=form)