from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, SelectField, IntegerField, BooleanField, PasswordField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from models import User


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already taken.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered.')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])


class CourseForm(FlaskForm):
    title = StringField('Course Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    category = StringField('Category')
    thumbnail = FileField('Thumbnail', validators=[FileAllowed(['jpg', 'png', 'jpeg', 'gif'])])


class ModuleForm(FlaskForm):
    title = StringField('Module Title', validators=[DataRequired()])
    description = TextAreaField('Description')
    order = IntegerField('Order', validators=[DataRequired()])


class ContentForm(FlaskForm):
    title = StringField('Content Title', validators=[DataRequired()])
    content_type = SelectField('Content Type', choices=[
        ('video', 'Video'),
        ('text', 'Text'),
        ('pdf', 'PDF')
    ])
    content_url = StringField('Video URL/Embed Code')
    content_text = TextAreaField('Text Content')
    order = IntegerField('Order', validators=[DataRequired()])


class QuizForm(FlaskForm):
    title = StringField('Quiz Title', validators=[DataRequired()])
    description = TextAreaField('Description')
    time_limit = IntegerField('Time Limit (minutes)')
    passing_score = IntegerField('Passing Score (%)', default=70)


class QuestionForm(FlaskForm):
    text = TextAreaField('Question', validators=[DataRequired()])
    question_type = SelectField('Question Type', choices=[
        ('multiple_choice', 'Multiple Choice'),
        ('true_false', 'True/False')
    ])
    options = TextAreaField('Options (one per line)')
    correct_answer = StringField('Correct Answer', validators=[DataRequired()])
    points = IntegerField('Points', default=1)


class AssignmentForm(FlaskForm):
    title = StringField('Assignment Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    due_date = StringField('Due Date (YYYY-MM-DD)')
    max_score = IntegerField('Maximum Score', default=100)