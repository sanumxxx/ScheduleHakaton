from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import UserMixin

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_approved = db.Column(db.Boolean, default=False)
    teacher = db.relationship('Teacher', backref='user', uselist=False)

class RegistrationRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=False)
    department = db.relationship('Department', backref='registration_requests')

class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=False)
    department = db.relationship('Department', backref='groups')

class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    faculty_id = db.Column(db.Integer, db.ForeignKey('faculty.id'), nullable=False)
    faculty = db.relationship('Faculty', backref='departments')

class Faculty(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

class Teacher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=False)
    department = db.relationship('Department', backref='teachers')
    subjects = db.relationship('Subject', secondary='teacher_subject', back_populates='teachers')

teacher_subject = db.Table(
    'teacher_subject',
    db.Column('teacher_id', db.Integer, db.ForeignKey('teacher.id'), primary_key=True),
    db.Column('subject_id', db.Integer, db.ForeignKey('subject.id'), primary_key=True)
)

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=False)
    department = db.relationship('Department', backref='subjects')
    teachers = db.relationship('Teacher', secondary='teacher_subject', back_populates='subjects')

class ScheduleEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'), nullable=True)
    weekday = db.Column(db.Integer, nullable=False)  # 1 - Понедельник, 2 - Вторник и т.д.
    lesson_time = db.Column(db.String(50), nullable=False)  # Например, "1 пара"
    week_type = db.Column(db.Integer, nullable=False)  # 1 - Зеленая неделя, 2 - Красная неделя
    room = db.Column(db.String(50), nullable=True)
    group = db.relationship('Group', backref='schedule_entries')
    subject = db.relationship('Subject', backref='schedule_entries')
    teacher = db.relationship('Teacher', backref='schedule_entries')

class Grade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    grade = db.Column(db.String(5), nullable=False)
    notified = db.Column(db.Boolean, default=False)
    grade_index = db.Column(db.Integer, nullable=False)  # Добавьте это поле
    date = db.Column(db.Date, nullable=False)
    student = db.relationship('Student', backref='grades')
    subject = db.relationship('Subject', backref='grades')

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref='messages')
    groups = db.relationship('Group', secondary='message_group', backref='messages')

message_group = db.Table(
    'message_group',
    db.Column('message_id', db.Integer, db.ForeignKey('message.id'), primary_key=True),
    db.Column('group_id', db.Integer, db.ForeignKey('group.id'), primary_key=True)
)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False)
    is_approved = db.Column(db.Boolean, default=False)
    telegram_id = db.Column(db.String(100), nullable=True)
    group = db.relationship('Group', backref='students')

