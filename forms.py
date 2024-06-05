from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, SelectMultipleField, IntegerField, TextAreaField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError, Optional
from models import User, Faculty, Department, Group, Teacher, Subject

class LoginForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired(), Length(min=2, max=80)])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')

class RegisterForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired(), Length(min=2, max=80)])
    password = PasswordField('Пароль', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Подтвердите пароль', validators=[DataRequired(), EqualTo('password')])
    department_id = SelectField('Кафедра', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Зарегистрироваться')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Пользователь с таким именем уже существует. Пожалуйста, выберите другое имя.')

class GroupForm(FlaskForm):
    name = StringField('Название группы', validators=[DataRequired(), Length(min=2, max=50)])
    department_id = SelectField('Кафедра', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Добавить группу')

class DepartmentForm(FlaskForm):
    name = StringField('Название кафедры', validators=[DataRequired(), Length(min=2, max=100)])
    faculty_id = SelectField('Факультет', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Добавить кафедру')

class FacultyForm(FlaskForm):
    name = StringField('Название факультета', validators=[DataRequired(), Length(min=2, max=100)])
    submit = SubmitField('Добавить факультет')

class SubjectForm(FlaskForm):
    name = StringField('Название дисциплины', validators=[DataRequired(), Length(min=2, max=100)])
    department_id = SelectField('Кафедра', coerce=int, validators=[DataRequired()])
    teacher_ids = SelectMultipleField('Преподаватели', coerce=int)
    submit = SubmitField('Добавить дисциплину')

class ScheduleEntryForm(FlaskForm):
    group_id = SelectField('Группа', coerce=int, validators=[DataRequired()])
    day = SelectField('День недели', coerce=int, choices=[
        (1, 'Понедельник'),
        (2, 'Вторник'),
        (3, 'Среда'),
        (4, 'Четверг'),
        (5, 'Пятница'),
        (6, 'Суббота')
    ], validators=[DataRequired()])
    subjects_green = SelectField('Зеленая неделя - Дисциплина', coerce=int, choices=[], validators=[Optional()])
    rooms_green = StringField('Зеленая неделя - Аудитория', validators=[Optional(), Length(min=0, max=50)])
    subjects_red = SelectField('Красная неделя - Дисциплина', coerce=int, choices=[], validators=[Optional()])
    rooms_red = StringField('Красная неделя - Аудитория', validators=[Optional(), Length(min=0, max=50)])
    submit = SubmitField('Сохранить расписание')


class GradeForm(FlaskForm):
    student_id = SelectField('Студент', coerce=int, validators=[DataRequired()])
    subject_id = SelectField('Дисциплина', coerce=int, validators=[DataRequired()])
    value = IntegerField('Оценка', validators=[DataRequired()])
    submit = SubmitField('Добавить оценку')

class MessageForm(FlaskForm):
    content = TextAreaField('Сообщение', validators=[DataRequired(), Length(min=1)])
    group_ids = SelectMultipleField('Группы', coerce=int)
    submit = SubmitField('Отправить сообщение')

class TeacherForm(FlaskForm):
    name = StringField('Имя преподавателя', validators=[DataRequired(), Length(min=2, max=100)])
    department_id = SelectField('Кафедра', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Добавить преподавателя')

class EditTeacherForm(FlaskForm):
    name = StringField('Имя преподавателя', validators=[DataRequired(), Length(min=2, max=100)])
    department_id = SelectField('Кафедра', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Сохранить изменения')
