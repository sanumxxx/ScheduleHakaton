from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from models import db, User, Group, Department, Faculty, Teacher, Subject, ScheduleEntry, RegistrationRequest, \
    Message, Student, Grade, Assignment
from forms import LoginForm, RegisterForm, GroupForm, DepartmentForm, FacultyForm, SubjectForm, ScheduleEntryForm, \
    MessageForm, EditTeacherForm, StudentForm, FlaskForm, AssignmentForm
from flask import jsonify
import qrcode, io
import requests
from datetime import date
from datetime import datetime





app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'  # Замените на свой секретный ключ
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://a0992402_sanumxxx:Yandex200515@sanumxxx.fun/a0992402_schedule'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def index():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    if current_user.is_admin:
        return redirect(url_for('admin_dashboard'))
    return redirect(url_for('teacher_dashboard'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            if not user.is_approved:
                flash('Ваша учетная запись ожидает подтверждения.', 'warning')
                return redirect(url_for('login'))
            login_user(user)
            flash('Вы успешно вошли в систему!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Неправильный логин или пароль.', 'danger')
    return render_template('login.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    form.department_id.choices = [(d.id, d.name) for d in Department.query.all()]
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        registration_request = RegistrationRequest(username=form.username.data, password=hashed_password,
                                                   department_id=form.department_id.data)
        db.session.add(registration_request)
        db.session.commit()
        flash('Ваша заявка на регистрацию отправлена. Ожидайте подтверждения администратора.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из системы!', 'success')
    return redirect(url_for('login'))


# Admin routes
@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        return redirect(url_for('index'))
    registration_request_count = RegistrationRequest.query.count()
    message_count = Message.query.count()
    return render_template('admin/dashboard.html', registration_request_count=registration_request_count,
                           message_count=message_count)


@app.route('/admin/manage_groups', methods=['GET', 'POST'])
@login_required
def manage_groups():
    if not current_user.is_admin:
        return redirect(url_for('index'))
    form = GroupForm()
    form.department_id.choices = [(d.id, d.name) for d in Department.query.all()]
    if form.validate_on_submit():
        group = Group(name=form.name.data, department_id=form.department_id.data)
        db.session.add(group)
        db.session.commit()
        flash('Группа успешно добавлена.', 'success')
        return redirect(url_for('manage_groups'))
    groups = Group.query.all()
    return render_template('admin/manage_groups.html', groups=groups, form=form)


@app.route('/admin/delete_group/<int:group_id>', methods=['GET', 'POST'])
@login_required
def delete_group(group_id):
    if not current_user.is_admin:
        return redirect(url_for('index'))
    group = Group.query.get_or_404(group_id)
    db.session.delete(group)
    db.session.commit()
    flash('Группа успешно удалена.', 'success')
    return redirect(url_for('manage_groups'))


@app.route('/admin/manage_departments', methods=['GET', 'POST'])
@login_required
def manage_departments():
    if not current_user.is_admin:
        return redirect(url_for('index'))
    form = DepartmentForm()
    form.faculty_id.choices = [(f.id, f.name) for f in Faculty.query.all()]
    if form.validate_on_submit():
        department = Department(name=form.name.data, faculty_id=form.faculty_id.data)
        db.session.add(department)
        db.session.commit()
        flash('Кафедра успешно добавлена.', 'success')
        return redirect(url_for('manage_departments'))
    departments = Department.query.all()
    return render_template('admin/manage_departments.html', departments=departments, form=form)


@app.route('/admin/delete_department/<int:department_id>', methods=['GET', 'POST'])
@login_required
def delete_department(department_id):
    if not current_user.is_admin:
        return redirect(url_for('index'))
    department = Department.query.get_or_404(department_id)
    db.session.delete(department)
    db.session.commit()
    flash('Кафедра успешно удалена.', 'success')
    return redirect(url_for('manage_departments'))


@app.route('/admin/manage_faculties', methods=['GET', 'POST'])
@login_required
def manage_faculties():
    if not current_user.is_admin:
        return redirect(url_for('index'))
    form = FacultyForm()
    if form.validate_on_submit():
        faculty = Faculty(name=form.name.data)
        db.session.add(faculty)
        db.session.commit()
        flash('Факультет успешно добавлен.', 'success')
        return redirect(url_for('manage_faculties'))
    faculties = Faculty.query.all()
    return render_template('admin/manage_faculties.html', faculties=faculties, form=form)


@app.route('/admin/delete_faculty/<int:faculty_id>', methods=['GET', 'POST'])
@login_required
def delete_faculty(faculty_id):
    if not current_user.is_admin:
        return redirect(url_for('index'))
    faculty = Faculty.query.get_or_404(faculty_id)
    db.session.delete(faculty)
    db.session.commit()
    flash('Факультет успешно удален.', 'success')
    return redirect(url_for('manage_faculties'))


@app.route('/admin/manage_subjects', methods=['GET', 'POST'])
@login_required
def manage_subjects():
    if not current_user.is_admin:
        return redirect(url_for('index'))
    form = SubjectForm()
    form.department_id.choices = [(d.id, d.name) for d in Department.query.all()]
    form.teacher_ids.choices = [(t.id, t.name) for t in Teacher.query.all()]
    if form.validate_on_submit():
        subject = Subject(name=form.name.data, department_id=form.department_id.data)
        db.session.add(subject)
        db.session.commit()
        for teacher_id in form.teacher_ids.data:
            teacher = Teacher.query.get(teacher_id)
            subject.teachers.append(teacher)
        db.session.commit()
        flash('Дисциплина успешно добавлена.', 'success')
        return redirect(url_for('manage_subjects'))
    subjects = Subject.query.all()
    return render_template('admin/manage_subjects.html', subjects=subjects, form=form)


@app.route('/admin/delete_subject/<int:subject_id>', methods=['GET', 'POST'])
@login_required
def delete_subject(subject_id):
    if not current_user.is_admin:
        return redirect(url_for('index'))

    subject = Subject.query.get_or_404(subject_id)

    # Удаляем все оценки, связанные с данной дисциплиной
    Grade.query.filter_by(subject_id=subject_id).delete()

    db.session.delete(subject)
    db.session.commit()

    flash('Дисциплина успешно удалена.', 'success')
    return redirect(url_for('manage_subjects'))


@app.route('/manage_schedule', methods=['GET', 'POST'])
@login_required
def manage_schedule():
    form = ScheduleEntryForm()
    form.group_id.choices = [(g.id, g.name) for g in Group.query.all()]
    form.day.choices = [(1, 'Понедельник'), (2, 'Вторник'), (3, 'Среда'), (4, 'Четверг'), (5, 'Пятница'), (6, 'Суббота')]
    form.subjects_green.choices = [(s.id, s.name) for s in Subject.query.all()]
    form.subjects_red.choices = [(s.id, s.name) for s in Subject.query.all()]

    if form.validate_on_submit():
        group_id = form.group_id.data
        day = form.day.data

        # Удаляем старые записи для выбранной группы и дня
        ScheduleEntry.query.filter_by(group_id=group_id, weekday=day).delete()

        for lesson_num in range(1, 6):
            green_subject_id = request.form.get(f'subjects_green_{lesson_num}')
            green_room = request.form.get(f'rooms_green_{lesson_num}')
            red_subject_id = request.form.get(f'subjects_red_{lesson_num}')
            red_room = request.form.get(f'rooms_red_{lesson_num}')

            if green_subject_id or green_room:
                green_entry = ScheduleEntry(
                    group_id=group_id,
                    subject_id=green_subject_id,
                    weekday=day,
                    lesson_time=f'{lesson_num} пара',
                    week_type=1,
                    room=green_room
                )
                db.session.add(green_entry)

            if red_subject_id or red_room:
                red_entry = ScheduleEntry(
                    group_id=group_id,
                    subject_id=red_subject_id,
                    weekday=day,
                    lesson_time=f'{lesson_num} пара',
                    week_type=2,
                    room=red_room
                )
                db.session.add(red_entry)

        db.session.commit()
        flash('Расписание обновлено', 'success')
        return redirect(url_for('manage_schedule'))

    schedule_entries_green = {lesson_num: None for lesson_num in range(1, 6)}
    schedule_entries_red = {lesson_num: None for lesson_num in range(1, 6)}

    if request.args.get('group_id') and request.args.get('day'):
        selected_group = int(request.args.get('group_id'))
        selected_day = int(request.args.get('day'))

        green_entries = ScheduleEntry.query.filter_by(group_id=selected_group, weekday=selected_day, week_type=1).all()
        red_entries = ScheduleEntry.query.filter_by(group_id=selected_group, weekday=selected_day, week_type=2).all()

        for entry in green_entries:
            lesson_num = int(entry.lesson_time.split()[0])
            schedule_entries_green[lesson_num] = entry

        for entry in red_entries:
            lesson_num = int(entry.lesson_time.split()[0])
            schedule_entries_red[lesson_num] = entry
    else:
        selected_group = None
        selected_day = None

    return render_template('admin/manage_schedule.html', form=form, selected_group=selected_group,
                           selected_day=selected_day, schedule_entries_green=schedule_entries_green,
                           schedule_entries_red=schedule_entries_red)


@app.route('/clear_schedule', methods=['POST'])
@login_required
def clear_schedule():
    group_id = request.args.get('group_id')
    day = request.args.get('day')

    if group_id and day:
        ScheduleEntry.query.filter_by(group_id=group_id, weekday=day).delete()
        db.session.commit()
        return jsonify(success=True)
    return jsonify(success=False), 400



@app.route('/admin/delete_schedule_entry/<int:entry_id>', methods=['GET', 'POST'])
@login_required
def delete_schedule_entry(entry_id):
    if not current_user.is_admin:
        return redirect(url_for('index'))
    entry = ScheduleEntry.query.get_or_404(entry_id)
    db.session.delete(entry)
    db.session.commit()
    flash('Запись в расписании успешно удалена.', 'success')
    return redirect(url_for('manage_schedule'))


@app.route('/admin/manage_teachers', methods=['GET', 'POST'])
@login_required
def manage_teachers():
    if not current_user.is_admin:
        return redirect(url_for('index'))
    teachers = Teacher.query.all()
    return render_template('admin/manage_teachers.html', teachers=teachers)


@app.route('/admin/edit_teacher/<int:teacher_id>', methods=['GET', 'POST'])
@login_required
def edit_teacher(teacher_id):
    if not current_user.is_admin:
        return redirect(url_for('index'))
    teacher = Teacher.query.get_or_404(teacher_id)
    form = EditTeacherForm(obj=teacher)
    form.department_id.choices = [(d.id, d.name) for d in Department.query.all()]
    if form.validate_on_submit():
        teacher.name = form.name.data
        teacher.department_id = form.department_id.data
        db.session.commit()
        flash('Данные преподавателя успешно обновлены.', 'success')
        return redirect(url_for('manage_teachers'))
    return render_template('admin/edit_teacher.html', form=form, teacher=teacher)


@app.route('/admin/delete_teacher/<int:teacher_id>', methods=['GET', 'POST'])
@login_required
def delete_teacher(teacher_id):
    if not current_user.is_admin:
        return redirect(url_for('index'))
    teacher = Teacher.query.get_or_404(teacher_id)
    db.session.delete(teacher)
    db.session.commit()
    flash('Преподаватель успешно удален.', 'success')
    return redirect(url_for('manage_teachers'))


@app.route('/admin/global_messages', methods=['GET', 'POST'])
@login_required
def global_messages():
    if not current_user.is_admin:
        return redirect(url_for('index'))
    form = MessageForm()
    form.group_ids.choices = [(g.id, g.name) for g in Group.query.all()]
    if form.validate_on_submit():
        message = Message(content=form.content.data, user_id=current_user.id)
        db.session.add(message)
        for group_id in form.group_ids.data:
            group = Group.query.get(group_id)
            message.groups.append(group)
        db.session.commit()
        flash('Сообщение отправлено.', 'success')
        return redirect(url_for('global_messages'))
    messages = Message.query.all()
    return render_template('admin/global_messages.html', messages=messages, form=form)


@app.route('/admin/delete_message/<int:message_id>', methods=['GET', 'POST'])
@login_required
def delete_message(message_id):
    if not current_user.is_admin:
        return redirect(url_for('index'))
    message = Message.query.get_or_404(message_id)
    db.session.delete(message)
    db.session.commit()
    flash('Сообщение успешно удалено.', 'success')
    return redirect(url_for('global_messages'))


@app.route('/approve_registration/<int:request_id>', methods=['POST'])
@login_required
def approve_registration(request_id):
    if not current_user.is_admin:
        return redirect(url_for('index'))

    registration_request = RegistrationRequest.query.get(request_id)
    if registration_request:
        # Создание нового пользователя
        new_user = User(username=registration_request.username,
                        password=registration_request.password,
                        is_approved=True)
        db.session.add(new_user)
        db.session.commit()

        # Создание нового преподавателя и связывание с пользователем
        new_teacher = Teacher(name=registration_request.username,
                              department_id=registration_request.department_id,
                              user_id=new_user.id)
        db.session.add(new_teacher)
        db.session.delete(registration_request)
        db.session.commit()

    return redirect(url_for('registration_requests'))



@app.route('/admin/reject_registration/<int:request_id>', methods=['POST'])
@login_required
def reject_registration(request_id):
    if not current_user.is_admin:
        return redirect(url_for('index'))
    registration_request = RegistrationRequest.query.get_or_404(request_id)
    db.session.delete(registration_request)
    db.session.commit()
    flash('Заявка на регистрацию отклонена.', 'success')
    return redirect(url_for('registration_requests'))


@app.route('/admin/registration_requests')
@login_required
def registration_requests():
    if not current_user.is_admin:
        return redirect(url_for('index'))
    requests = RegistrationRequest.query.all()
    return render_template('admin/registration_requests.html', requests=requests)

# Teacher routes
# Teacher routes
@app.route('/teacher/dashboard')
@login_required
def teacher_dashboard():
    teacher = Teacher.query.filter_by(user_id=current_user.id).first()
    if not teacher:
        flash('Преподаватель не найден', 'danger')
        return redirect(url_for('index'))
    # Здесь изменяем запрос, чтобы получить количество сообщений, относящихся к группам, в которых находится преподаватель
    message_count = Message.query.filter(Message.groups.any(Group.department_id == teacher.department_id)).count()
    return render_template('teacher/dashboard.html', message_count=message_count)


@app.route('/teacher/view_schedule', methods=['GET'])
@login_required
def view_schedule():
    teacher = Teacher.query.filter_by(user_id=current_user.id).first()
    if not teacher:
        flash('Вы не прикреплены к преподавателю.', 'danger')
        return redirect(url_for('index'))

    selected_group = request.args.get('group_id', type=int)
    selected_week_type = request.args.get('week_type', type=int, default=1)

    groups = Group.query.filter_by(department_id=teacher.department_id).all()
    schedule = {}

    if selected_group:
        for day in range(1, 7):
            schedule[day] = {lesson_num: None for lesson_num in range(1, 6)}
            entries = ScheduleEntry.query.filter_by(
                group_id=selected_group,
                weekday=day,
                week_type=selected_week_type
            ).all()
            for entry in entries:
                lesson_num = int(entry.lesson_time.split()[0])
                schedule[day][lesson_num] = entry

    return render_template(
        'teacher/view_schedule.html',
        groups=groups,
        schedule=schedule,
        selected_group=selected_group,
        selected_week_type=selected_week_type
    )


@app.route('/teacher/get_schedule', methods=['GET'])
@login_required
def get_schedule():
    if current_user.teacher is None:
        return jsonify({'error': 'Вы не являетесь преподавателем.'}), 403

    group_id = request.args.get('group_id', type=int)
    week_type = request.args.get('week_type', type=int)

    schedule_entries = ScheduleEntry.query.filter_by(group_id=group_id, week_type=week_type).all()
    schedule = {i: None for i in range(1, 6)}
    for entry in schedule_entries:
        lesson_num = int(entry.lesson_time.split()[0])
        schedule[lesson_num] = {
            'subject': entry.subject.name if entry.subject else '',
            'room': entry.room
        }

    return jsonify(schedule)


@app.route('/teacher/messages', methods=['GET', 'POST'])
@login_required
def teacher_messages():
    teacher = Teacher.query.filter_by(user_id=current_user.id).first()

    if not teacher:
        flash('You are not a teacher', 'danger')
        return redirect(url_for('index'))

    form = MessageForm()

    if hasattr(teacher, 'department'):
        form.group_ids.choices = [(g.id, g.name) for g in teacher.department.groups]
    else:
        form.group_ids.choices = []

    if form.validate_on_submit():
        message = Message(
            content=form.content.data,
            user_id=current_user.id
        )
        db.session.add(message)
        db.session.commit()

        for group_id in form.group_ids.data:
            group = Group.query.get(group_id)
            group.messages.append(message)

        db.session.commit()

        flash('Message sent successfully', 'success')
        return redirect(url_for('teacher_messages'))

    return render_template('teacher/teacher_messages.html', form=form)


@app.route('/students')
@login_required
def students():
    groups = Group.query.all()
    return render_template('students.html', groups=groups)


@app.route('/teacher/students/<int:group_id>', methods=['GET', 'POST'])
@login_required
def view_students(group_id):
    group = Group.query.get_or_404(group_id)
    students = group.students
    form = StudentForm()

    if form.validate_on_submit():
        student_id = request.form.get('student_id')
        if student_id:
            # Редактирование существующего студента
            student = Student.query.get_or_404(student_id)
            student.first_name = form.first_name.data
            student.last_name = form.last_name.data
            student.email = form.email.data
            student.group_id = form.group_id.data
            db.session.commit()
            flash('Данные студента обновлены', 'success')
        else:
            # Добавление нового студента
            student = Student(
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                email=form.email.data,
                group_id=group_id
            )
            db.session.add(student)
            db.session.commit()
            flash('Студент добавлен', 'success')

        return redirect(url_for('view_students', group_id=group_id))

    return render_template('teacher/view_students.html', group=group, students=students, form=form)
@app.route('/teacher/students/add/<int:group_id>', methods=['GET', 'POST'])
@login_required
def add_student(group_id):
    group = Group.query.get_or_404(group_id)
    form = StudentForm()

    if form.validate_on_submit():
        student = Student(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data,
            group_id=group_id
        )
        db.session.add(student)
        db.session.commit()
        flash('Студент добавлен', 'success')
        return redirect(url_for('view_students', group_id=group_id))

    return render_template('teacher/add_student.html', form=form, group=group)


@app.route('/teacher/students/edit/<int:student_id>', methods=['GET', 'POST'])
@login_required
def edit_student(student_id):
    student = Student.query.get_or_404(student_id)
    form = StudentForm(obj=student)

    if form.validate_on_submit():
        student.first_name = form.first_name.data
        student.last_name = form.last_name.data
        student.email = form.email.data
        student.group_id = form.group_id.data
        db.session.commit()
        flash('Данные студента обновлены', 'success')
        return redirect(url_for('view_students', group_id=student.group_id))

    return render_template('teacher/edit_student.html', form=form)


@app.route('/teacher/delete_student/<int:student_id>', methods=['POST'])
@login_required
def delete_student(student_id):
    student = Student.query.get_or_404(student_id)
    group_id = student.group_id  # Получаем ID группы студента

    # Удаляем все оценки, связанные с данным студентом
    Grade.query.filter_by(student_id=student_id).delete()

    db.session.delete(student)
    db.session.commit()

    return redirect(url_for('manage_students', group_id=group_id))


@app.route('/teacher/students')
@login_required
def teacher_students():
    teacher = Teacher.query.filter_by(user_id=current_user.id).first()
    if not teacher:
        flash('Вы не являетесь преподавателем', 'danger')
        return redirect(url_for('teacher_dashboard'))

    groups = Group.query.filter_by(department_id=teacher.department_id).all()
    return render_template('teacher/students.html', groups=groups)


@app.route('/teacher/students/<int:group_id>', methods=['GET', 'POST'])
@login_required
def manage_students(group_id):
    group = Group.query.get_or_404(group_id)
    form = StudentForm()

    if form.validate_on_submit():
        student = Student(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data,
            group_id=form.group_id.data
        )
        db.session.add(student)
        db.session.commit()
        flash('Студент добавлен', 'success')
        return redirect(url_for('manage_students', group_id=group_id))

    students = Student.query.filter_by(group_id=group_id).all()
    return render_template('teacher/view_students.html', group=group, students=students, form=form)


@app.route('/generate_registration_link/<int:student_id>')
def generate_registration_link(student_id):
    student = Student.query.get(student_id)
    if not student:
        return "Student not found", 404

    qr_img = generate_qr_code(student_id)
    img_io = io.BytesIO()
    qr_img.save(img_io, 'PNG')
    img_io.seek(0)

    return render_template('generate_registration_link.html', student=student, qr_code_data=img_io)


def generate_qr_code(student_id):
    base_url = "https://t.me/kafedra_it_bot?start=register_"
    qr_data = f"{base_url}{student_id}"
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    return img


@app.route('/qr_code/<int:student_id>')
def qr_code(student_id):
    student = Student.query.get(student_id)
    if not student:
        return "Student not found", 404

    qr_img = generate_qr_code(student_id)
    img_io = io.BytesIO()
    qr_img.save(img_io, 'PNG')
    img_io.seek(0)

    return send_file(img_io, mimetype='image/png')


@app.route('/teacher/grades', methods=['GET'])
@login_required
def teacher_grades():
    teacher = current_user.teacher
    subjects = teacher.subjects  # Получаем все связанные объекты Subject
    return render_template('teacher/grades.html', subjects=subjects)

@app.route('/teacher/grades/<int:subject_id>')
@login_required
def select_group(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    groups = subject.department.groups
    return render_template('teacher/select_group.html', subject=subject, groups=groups)
@app.route('/teacher/grades/<int:subject_id>/<int:group_id>', methods=['GET', 'POST'])
@login_required
def grade_journal(subject_id, group_id):
    subject = Subject.query.get_or_404(subject_id)
    group = Group.query.get_or_404(group_id)
    students = group.students

    form = FlaskForm()  # создайте экземпляр формы

    if request.method == 'POST':
        for student in students:
            grade_value = request.form.get(f'grade_{student.id}')
            if grade_value:
                grade = Grade(
                    student_id=student.id,
                    subject_id=subject_id,
                    grade=grade_value,
                    date=date.today()
                )
                db.session.add(grade)
        db.session.commit()
        flash('Оценки сохранены!', 'success')
        return redirect(url_for('grade_journal', subject_id=subject_id, group_id=group_id))

    return render_template('teacher/grade_journal.html', subject=subject, group=group, students=students, form=form)


@app.route('/save_grades', methods=['POST'])
def save_grades():
    try:
        grades = request.get_json()
        print(f"Received grades: {grades}")

        for grade_data in grades:
            try:
                student_id = grade_data.get('student_id')
                assignment_id = grade_data.get('assignment_id')
                grade_value = grade_data.get('grade')

                print(f"Student ID: {student_id}, Assignment ID: {assignment_id}, Grade Value: {grade_value}")

                if student_id is None or assignment_id is None or grade_value is None:
                    print(f"Invalid grade data: {grade_data}")
                    continue

                print(f"Processing grade: student_id={student_id}, assignment_id={assignment_id}, grade_value={grade_value}")

                grade_entry = Grade.query.filter_by(
                    student_id=student_id,
                    assignment_id=assignment_id
                ).first()

                if grade_entry:
                    if grade_value:
                        grade_entry.grade = grade_value
                    else:
                        db.session.delete(grade_entry)
                elif grade_value:
                    grade_entry = Grade(
                        student_id=student_id,
                        assignment_id=assignment_id,
                        grade=grade_value,
                        date=datetime.now().date()
                    )
                    db.session.add(grade_entry)

            except KeyError as e:
                print(f"Missing key in grade data: {e}")
                continue

        db.session.commit()
        print("Grades saved successfully")

        # Отправка уведомлений студентам
        for grade_data in grades:
            try:
                student_id = grade_data.get('student_id')
                assignment_id = grade_data.get('assignment_id')
                grade_value = grade_data.get('grade')

                if student_id is None or assignment_id is None or grade_value is None:
                    print(f"Invalid grade data for notification: {grade_data}")
                    continue

                grade_entry = Grade.query.filter_by(
                    student_id=student_id,
                    assignment_id=assignment_id,
                    grade=grade_value
                ).first()

                if grade_entry and not grade_entry.notified:
                    student = Student.query.get(student_id)
                    assignment = Assignment.query.get(assignment_id)
                    teacher = current_user.teacher

                    if student and assignment and teacher:
                        if student.telegram_id:
                            message = f"*{teacher.name}* поставил оценку {grade_value} за задание '*{assignment.title}*' по предмету '*{assignment.subject.name}*'."
                            send_grade_notification(student.telegram_id, message)
                            print(f"Notification sent to student {student.id}")
                        else:
                            print(f"Student {student.id} does not have a Telegram ID")
                    else:
                        print(f"Invalid data for notification: student={student}, assignment={assignment}, teacher={teacher}")

                    grade_entry.notified = True
                    db.session.commit()

            except KeyError as e:
                print(f"Missing key in grade data for notification: {e}")
                continue

        return jsonify(success=True)

    except Exception as e:
        print(f"Error in /save_grades: {str(e)}")
        db.session.rollback()
        return jsonify(success=False, error=str(e)), 500
def send_grade_notification(telegram_id, message):
    try:
        bot_token = '6897033821:AAE80aF2-Kvn3dF8CSHH_PPMDoyulJMiLoo'
        url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
        params = {
            'chat_id': telegram_id,
            'text': message,
            'parse_mode': 'Markdown'  # Указываем использование разметки Markdown
        }
        response = requests.post(url, json=params)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Failed to send message to {telegram_id}. Error: {str(e)}")

@app.route('/teacher/assignments', methods=['GET', 'POST'])
@login_required
def assignments():
    teacher = current_user.teacher
    assignments = Assignment.query.join(Subject).filter(Subject.department_id == teacher.department_id).all()
    create_form = AssignmentForm()

    create_form.subject_id.choices = [(s.id, s.name) for s in teacher.subjects]

    if create_form.validate_on_submit():
        assignment = Assignment(
            title=create_form.title.data,
            description=create_form.description.data,
            subject_id=create_form.subject_id.data
        )
        db.session.add(assignment)
        db.session.commit()
        flash('Задание создано', 'success')
        return redirect(url_for('assignments'))

    return render_template('teacher/assignments.html', assignments=assignments, create_form=create_form)

@app.route('/teacher/assignments/edit/<int:assignment_id>', methods=['POST'])
@login_required
def edit_assignment(assignment_id):
    teacher = current_user.teacher
    assignment = Assignment.query.get_or_404(assignment_id)

    if assignment.subject.department_id != teacher.department_id:
        flash('Вы не можете редактировать задание для этого предмета', 'danger')
        return redirect(url_for('assignments'))

    edit_form = AssignmentForm(request.form, obj=assignment)
    edit_form.subject_id.choices = [(s.id, s.name) for s in teacher.subjects]

    if edit_form.validate_on_submit():
        assignment.title = edit_form.title.data
        assignment.description = edit_form.description.data
        assignment.subject_id = edit_form.subject_id.data
        db.session.commit()
        flash('Задание обновлено', 'success')
        return redirect(url_for('assignments'))

    flash('Ошибка при обновлении задания', 'danger')
    return redirect(url_for('assignments'))@app.route('/teacher/assignments/create', methods=['GET', 'POST'])

@login_required
def create_assignment():
    form = AssignmentForm()
    if form.validate_on_submit():
        assignment = Assignment(
            title=form.title.data,
            description=form.description.data,
            subject_id=form.subject_id.data
        )
        db.session.add(assignment)
        db.session.commit()
        flash('Задание создано', 'success')
        return redirect(url_for('assignments'))
    return render_template('teacher/create_assignment.html', form=form)


@app.route('/teacher/assignments/delete/<int:assignment_id>', methods=['POST'])
@login_required
def delete_assignment(assignment_id):
    assignment = Assignment.query.get_or_404(assignment_id)
    db.session.delete(assignment)
    db.session.commit()
    flash('Задание удалено', 'success')
    return redirect(url_for('assignments'))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(username='admin').first():
            hashed_password = bcrypt.generate_password_hash('admin').decode('utf-8')
            admin = User(username='admin', password=hashed_password, is_admin=True, is_approved=True)
            db.session.add(admin)
            db.session.commit()
    app.run(host='127.0.0.1',port=5000,  debug=True)
