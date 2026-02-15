# add_sample_data.py
from app import app, db
from models import User, Course, Module, Content
from werkzeug.security import generate_password_hash
from datetime import datetime


def add_sample_data():
    with app.app_context():
        # Check if we already have an instructor
        instructor = User.query.filter_by(is_instructor=True).first()

        if not instructor:
            # Create a sample instructor
            instructor = User(
                username='dr_smith',
                email='instructor@example.com',
                password=generate_password_hash('password123'),
                is_instructor=True
            )
            db.session.add(instructor)
            db.session.commit()
            print("Created sample instructor: dr_smith (password: password123)")
        else:
            print(f"Using existing instructor: {instructor.username}")

        # Check if we already have courses
        if Course.query.count() == 0:
            # Sample Course 1: Python Programming
            course1 = Course(
                title='Python Programming for Beginners',
                description='Learn Python programming from scratch. This course covers variables, data types, control flow, functions, and more. Perfect for absolute beginners!',
                category='Programming',
                instructor_id=instructor.id,
                created_at=datetime.utcnow()
            )
            db.session.add(course1)
            db.session.flush()  # To get course1.id

            # Add modules for course1
            module1 = Module(
                title='Introduction to Python',
                description='Get started with Python programming language',
                order=1,
                course_id=course1.id
            )
            db.session.add(module1)
            db.session.flush()

            # Add content for module1
            content1 = Content(
                title='What is Python?',
                content_type='video',
                content_url='https://www.youtube.com/embed/_uQrJ0TkZlc',
                content_text='',
                order=1,
                module_id=module1.id
            )
            db.session.add(content1)

            content2 = Content(
                title='Installing Python',
                content_type='text',
                content_url='',
                content_text='To install Python, visit python.org and download the latest version for your operating system. Follow the installation instructions and make sure to check "Add Python to PATH" during installation.',
                order=2,
                module_id=module1.id
            )
            db.session.add(content2)

            # Module 2
            module2 = Module(
                title='Python Basics',
                description='Learn the basic concepts of Python programming',
                order=2,
                course_id=course1.id
            )
            db.session.add(module2)
            db.session.flush()

            content3 = Content(
                title='Variables and Data Types',
                content_type='video',
                content_url='https://www.youtube.com/embed/cQT33yu9pY8',
                content_text='',
                order=1,
                module_id=module2.id
            )
            db.session.add(content3)

            # Sample Course 2: Web Development
            course2 = Course(
                title='Complete Web Development Bootcamp',
                description='Master HTML, CSS, JavaScript, and more. Build real-world projects and become a full-stack web developer.',
                category='Web Development',
                instructor_id=instructor.id,
                created_at=datetime.utcnow()
            )
            db.session.add(course2)
            db.session.flush()

            module3 = Module(
                title='HTML Fundamentals',
                description='Learn the structure of web pages',
                order=1,
                course_id=course2.id
            )
            db.session.add(module3)
            db.session.flush()

            content4 = Content(
                title='Introduction to HTML',
                content_type='video',
                content_url='https://www.youtube.com/embed/UB1O30fR-EE',
                content_text='',
                order=1,
                module_id=module3.id
            )
            db.session.add(content4)

            # Sample Course 3: Data Science
            course3 = Course(
                title='Data Science Fundamentals',
                description='Learn data analysis, visualization, and machine learning with Python. Perfect for aspiring data scientists.',
                category='Data Science',
                instructor_id=instructor.id,
                created_at=datetime.utcnow()
            )
            db.session.add(course3)

            # Sample Course 4: Business Management
            course4 = Course(
                title='Business Management 101',
                description='Learn the essentials of business management, leadership, and organizational behavior.',
                category='Business',
                instructor_id=instructor.id,
                created_at=datetime.utcnow()
            )
            db.session.add(course4)

            # Sample Course 5: Digital Marketing
            course5 = Course(
                title='Digital Marketing Masterclass',
                description='Master SEO, social media marketing, content marketing, and more. Grow your online presence.',
                category='Marketing',
                instructor_id=instructor.id,
                created_at=datetime.utcnow()
            )
            db.session.add(course5)

            db.session.commit()
            print("Sample courses added successfully!")
        else:
            print(f"Found {Course.query.count()} existing courses. No new courses added.")


if __name__ == '__main__':
    add_sample_data()
    print("Sample data addition complete!")