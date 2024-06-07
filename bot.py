import telebot
from telebot import types
from flask import Flask
from models import db, Student
from sqlalchemy.exc import SQLAlchemyError

API_TOKEN = '6897033821:AAE80aF2-Kvn3dF8CSHH_PPMDoyulJMiLoo'
bot = telebot.TeleBot(API_TOKEN)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://a0992402_sanumxxx:Yandex200515@sanumxxx.fun/a0992402_schedule'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

def get_student_by_telegram_id(telegram_id):
    return Student.query.filter_by(telegram_id=telegram_id).first()

def get_student_by_id(student_id):
    return Student.query.get(student_id)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    with app.app_context():
        student = get_student_by_telegram_id(message.from_user.id)
        if student:
            bot.reply_to(message, f"Добро пожаловать, {student.first_name} {student.last_name}!")
            send_schedule_button(message, student.group_id)
            return

    args = message.text.split()
    if len(args) > 1 and args[1].startswith('register_'):
        student_id = int(args[1].split('_')[1])
        try:
            with app.app_context():
                student = get_student_by_id(student_id)
                if student:
                    print(f"Registering student ID {student_id} with Telegram ID {message.from_user.id}")
                    student.telegram_id = str(message.from_user.id)
                    student.is_approved = True  # is_approved should be a boolean
                    db.session.commit()
                    print(f"Student {student_id} registered successfully: telegram_id={student.telegram_id}, is_approved={student.is_approved}")
                    bot.reply_to(message, f"Успешная регистрация для {student.first_name} {student.last_name}!")
                    send_schedule_button(message, student.group_id)
                else:
                    bot.reply_to(message, "Неправильный ID. Свяжитесь с вашим преподавателем")
        except SQLAlchemyError as e:
            print(f"SQLAlchemy Error: {e}")
            db.session.rollback()
    else:
        bot.reply_to(message, "Добро пожаловать, чтобы зарегистрироватся, свяжитесь с вашим преподавателем")

def send_schedule_button(message, group_id):
    keyboard = types.InlineKeyboardMarkup()
    web_app_info = types.WebAppInfo(url=f"https://sanumxxx.fun/?group_id={group_id}")
    schedule_button = types.InlineKeyboardButton(text="Расписание", web_app=web_app_info)
    keyboard.add(schedule_button)
    bot.send_message(message.chat.id, "Выберите действие:", reply_markup=keyboard)

def start_bot():
    bot.polling()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    start_bot()
