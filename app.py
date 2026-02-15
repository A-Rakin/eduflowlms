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