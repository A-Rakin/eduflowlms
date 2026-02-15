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


@app.route('/course/<int:course_id>')
def view_course(course_id):
    course = Course.query.get_or_404(course_id)
    is_enrolled = False
    if current_user.is_authenticated:
        enrollment = Enrollment.query.filter_by(
            student_id=current_user.id,
            course_id=course_id
        ).first()
        is_enrolled = enrollment is not None

    return render_template('course.html', course=course, is_enrolled=is_enrolled)


@app.route('/course/<int:course_id>/manage')
@login_required
def manage_course(course_id):
    course = Course.query.get_or_404(course_id)
    if course.instructor_id != current_user.id:
        abort(403)

    return render_template('manage_course.html', course=course)


@app.route('/course/<int:course_id>/enroll')
@login_required
def enroll_course(course_id):
    course = Course.query.get_or_404(course_id)

    # Check if already enrolled
    existing = Enrollment.query.filter_by(
        student_id=current_user.id,
        course_id=course_id
    ).first()

    if not existing:
        enrollment = Enrollment(
            student_id=current_user.id,
            course_id=course_id
        )
        db.session.add(enrollment)
        db.session.commit()
        flash(f'You have successfully enrolled in {course.title}!', 'success')

    return redirect(url_for('view_course', course_id=course_id))


# Module Management
@app.route('/course/<int:course_id>/module/add', methods=['GET', 'POST'])
@login_required
def add_module(course_id):
    course = Course.query.get_or_404(course_id)
    if course.instructor_id != current_user.id:
        abort(403)

    form = ModuleForm()
    if form.validate_on_submit():
        module = Module(
            title=form.title.data,
            description=form.description.data,
            order=form.order.data,
            course_id=course_id
        )
        db.session.add(module)
        db.session.commit()
        flash('Module added successfully!', 'success')
        return redirect(url_for('manage_course', course_id=course_id))

    return render_template('add_module.html', form=form, course=course)


# Content Management
@app.route('/module/<int:module_id>/content/add', methods=['GET', 'POST'])
@login_required
def add_content(module_id):
    module = Module.query.get_or_404(module_id)
    if module.course.instructor_id != current_user.id:
        abort(403)

    form = ContentForm()
    if form.validate_on_submit():
        content = Content(
            title=form.title.data,
            content_type=form.content_type.data,
            content_url=form.content_url.data,
            content_text=form.content_text.data,
            order=form.order.data,
            module_id=module_id
        )
        db.session.add(content)
        db.session.commit()
        flash('Content added successfully!', 'success')
        return redirect(url_for('manage_course', course_id=module.course.id))

    return render_template('add_content.html', form=form, module=module)


# Quiz Management
@app.route('/module/<int:module_id>/quiz/add', methods=['GET', 'POST'])
@login_required
def add_quiz(module_id):
    module = Module.query.get_or_404(module_id)
    if module.course.instructor_id != current_user.id:
        abort(403)

    form = QuizForm()
    if form.validate_on_submit():
        quiz = Quiz(
            title=form.title.data,
            description=form.description.data,
            time_limit=form.time_limit.data,
            passing_score=form.passing_score.data,
            module_id=module_id
        )
        db.session.add(quiz)
        db.session.commit()
        flash('Quiz added successfully!', 'success')
        return redirect(url_for('manage_quiz', quiz_id=quiz.id))

    return render_template('add_quiz.html', form=form, module=module)


@app.route('/quiz/<int:quiz_id>/manage')
@login_required
def manage_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    if quiz.module.course.instructor_id != current_user.id:
        abort(403)

    return render_template('manage_quiz.html', quiz=quiz)


@app.route('/quiz/<int:quiz_id>/question/add', methods=['GET', 'POST'])
@login_required
def add_question(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    if quiz.module.course.instructor_id != current_user.id:
        abort(403)

    form = QuestionForm()
    if form.validate_on_submit():
        options = None
        if form.question_type.data == 'multiple_choice':
            options = json.dumps([opt.strip() for opt in form.options.data.split('\n') if opt.strip()])

        question = Question(
            text=form.text.data,
            question_type=form.question_type.data,
            options=options,
            correct_answer=form.correct_answer.data,
            points=form.points.data,
            quiz_id=quiz_id
        )
        db.session.add(question)
        db.session.commit()
        flash('Question added successfully!', 'success')
        return redirect(url_for('manage_quiz', quiz_id=quiz_id))

    return render_template('add_question.html', form=form, quiz=quiz)


# Assignment Management
@app.route('/module/<int:module_id>/assignment/add', methods=['GET', 'POST'])
@login_required
def add_assignment(module_id):
    module = Module.query.get_or_404(module_id)
    if module.course.instructor_id != current_user.id:
        abort(403)

    form = AssignmentForm()
    if form.validate_on_submit():
        due_date = None
        if form.due_date.data:
            due_date = datetime.strptime(form.due_date.data, '%Y-%m-%d')

        assignment = Assignment(
            title=form.title.data,
            description=form.description.data,
            due_date=due_date,
            max_score=form.max_score.data,
            module_id=module_id
        )
        db.session.add(assignment)
        db.session.commit()
        flash('Assignment added successfully!', 'success')
        return redirect(url_for('manage_course', course_id=module.course.id))

    return render_template('add_assignment.html', form=form, module=module)


# Learning Routes
@app.route('/learn/<int:course_id>/module/<int:module_id>/content/<int:content_id>')
@login_required
def view_content(course_id, module_id, content_id):
    course = Course.query.get_or_404(course_id)
    module = Module.query.get_or_404(module_id)
    content = Content.query.get_or_404(content_id)

    # Check enrollment
    enrollment = Enrollment.query.filter_by(
        student_id=current_user.id,
        course_id=course_id
    ).first_or_404()

    # Mark as completed
    completion = ContentCompletion.query.filter_by(
        user_id=current_user.id,
        content_id=content_id
    ).first()

    if not completion:
        completion = ContentCompletion(
            user_id=current_user.id,
            content_id=content_id
        )
        db.session.add(completion)

        # Update progress
        progress = Progress(
            enrollment_id=enrollment.id,
            content_id=content_id,
            completed=True,
            completed_at=datetime.utcnow()
        )
        db.session.add(progress)
        db.session.commit()

    return render_template('view_content.html', course=course, module=module, content=content)


@app.route('/quiz/<int:quiz_id>/take', methods=['GET', 'POST'])
@login_required
def take_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)

    if request.method == 'POST':
        score = 0
        total_points = 0
        answers = {}

        for question in quiz.questions:
            answer = request.form.get(f'question_{question.id}')
            answers[str(question.id)] = answer

            if answer == question.correct_answer:
                score += question.points
            total_points += question.points

        final_score = (score / total_points * 100) if total_points > 0 else 0

        attempt = QuizAttempt(
            user_id=current_user.id,
            quiz_id=quiz_id,
            score=final_score,
            answers=json.dumps(answers),
            completed_at=datetime.utcnow()
        )
        db.session.add(attempt)
        db.session.commit()

        flash(f'Quiz completed! Your score: {final_score:.1f}%', 'success')
        return redirect(url_for('view_course', course_id=quiz.module.course.id))

    return render_template('take_quiz.html', quiz=quiz)


@app.route('/assignment/<int:assignment_id>/submit', methods=['GET', 'POST'])
@login_required
def submit_assignment(assignment_id):
    assignment = Assignment.query.get_or_404(assignment_id)

    if request.method == 'POST':
        submission_text = request.form.get('submission_text')
        file = request.files.get('file')

        file_url = None
        if file and file.filename:
            filename = secure_filename(f"{uuid.uuid4()}_{file.filename}")
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            file_url = filename

        submission = Submission(
            user_id=current_user.id,
            assignment_id=assignment_id,
            submission_text=submission_text,
            file_url=file_url,
            submitted_at=datetime.utcnow()
        )
        db.session.add(submission)
        db.session.commit()

        flash('Assignment submitted successfully!', 'success')
        return redirect(url_for('view_course', course_id=assignment.module.course.id))

    return render_template('submit_assignment.html', assignment=assignment)


# Certificate Generation
@app.route('/certificate/<int:course_id>/generate')
@login_required
def generate_certificate(course_id):
    course = Course.query.get_or_404(course_id)
    enrollment = Enrollment.query.filter_by(
        student_id=current_user.id,
        course_id=course_id
    ).first_or_404()

    # Check if course completed (all contents viewed)
    total_contents = Content.query.join(Module).filter(Module.course_id == course_id).count()
    completed_contents = ContentCompletion.query.filter_by(user_id=current_user.id).count()

    if total_contents > completed_contents:
        flash('Please complete all course content before generating certificate.', 'warning')
        return redirect(url_for('view_course', course_id=course_id))

    # Check if certificate already exists
    existing = Certificate.query.filter_by(
        user_id=current_user.id,
        course_id=course_id
    ).first()

    if existing:
        return send_file(existing.certificate_url, as_attachment=True)

    # Generate new certificate
    cert_number = f"CERT-{uuid.uuid4().hex[:8].upper()}"
    filename = f"certificate_{current_user.id}_{course_id}.pdf"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    # Create PDF certificate
    c = canvas.Canvas(filepath, pagesize=letter)
    c.setFont("Helvetica-Bold", 24)
    c.drawString(200, 500, "Certificate of Completion")
    c.setFont("Helvetica", 16)
    c.drawString(150, 400, f"This certifies that {current_user.username}")
    c.drawString(150, 350, f"has successfully completed the course")
    c.setFont("Helvetica-Bold", 20)
    c.drawString(150, 300, course.title)
    c.setFont("Helvetica", 12)
    c.drawString(150, 200, f"Certificate Number: {cert_number}")
    c.drawString(150, 170, f"Issued on: {datetime.now().strftime('%B %d, %Y')}")
    c.save()

    certificate = Certificate(
        user_id=current_user.id,
        course_id=course_id,
        certificate_url=filepath,
        certificate_number=cert_number
    )
    db.session.add(certificate)

    # Mark course as completed
    enrollment.completed = True
    enrollment.completed_at = datetime.utcnow()
    db.session.commit()

    return send_file(filepath, as_attachment=True)


# Forum Routes
@app.route('/course/<int:course_id>/forum')
@login_required
def forum(course_id):
    course = Course.query.get_or_404(course_id)
    threads = ForumThread.query.filter_by(course_id=course_id).order_by(ForumThread.created_at.desc()).all()
    return render_template('forum.html', course=course, threads=threads)


@app.route('/course/<int:course_id>/thread/new', methods=['GET', 'POST'])
@login_required
def new_thread(course_id):
    course = Course.query.get_or_404(course_id)

    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')

        thread = ForumThread(
            title=title,
            content=content,
            user_id=current_user.id,
            course_id=course_id
        )
        db.session.add(thread)
        db.session.commit()

        flash('Thread created successfully!', 'success')
        return redirect(url_for('forum', course_id=course_id))

    return render_template('new_thread.html', course=course)


@app.route('/thread/<int:thread_id>')
@login_required
def view_thread(thread_id):
    thread = ForumThread.query.get_or_404(thread_id)
    return render_template('view_thread.html', thread=thread)


@app.route('/thread/<int:thread_id>/post', methods=['POST'])
@login_required
def add_post(thread_id):
    thread = ForumThread.query.get_or_404(thread_id)
    content = request.form.get('content')

    post = ForumPost(
        content=content,
        user_id=current_user.id,
        thread_id=thread_id
    )
    db.session.add(post)
    db.session.commit()

    return redirect(url_for('view_thread', thread_id=thread_id))


# API Routes for Progress Tracking
@app.route('/api/progress/<int:content_id>', methods=['POST'])
@login_required
def mark_content_complete(content_id):
    content = Content.query.get_or_404(content_id)

    completion = ContentCompletion.query.filter_by(
        user_id=current_user.id,
        content_id=content_id
    ).first()

    if not completion:
        completion = ContentCompletion(
            user_id=current_user.id,
            content_id=content_id
        )
        db.session.add(completion)
        db.session.commit()

        return jsonify({'status': 'success', 'message': 'Content marked as complete'})

    return jsonify({'status': 'info', 'message': 'Already completed'})


@app.route('/api/course/<int:course_id>/progress')
@login_required
def get_course_progress(course_id):
    total_contents = Content.query.join(Module).filter(Module.course_id == course_id).count()
    completed_contents = ContentCompletion.query.filter_by(user_id=current_user.id).count()

    progress_percentage = (completed_contents / total_contents * 100) if total_contents > 0 else 0

    return jsonify({
        'total': total_contents,
        'completed': completed_contents,
        'percentage': progress_percentage
    })


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)