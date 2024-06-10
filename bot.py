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

def send_schedule_button(message, group_id, student_id=None):
    keyboard = types.InlineKeyboardMarkup()
    schedule_web_app = types.WebAppInfo(url=f"https://sanumxxx.fun/?group_id={group_id}")
    schedule_button = types.InlineKeyboardButton(text="Расписание", web_app=schedule_web_app)

    if student_id:
        grades_web_app = types.WebAppInfo(url=f"https://sanumxxx.fun/grades.php?student_id={student_id}")
        grades_button = types.InlineKeyboardButton(text="Оценки", web_app=grades_web_app)
        keyboard.add(schedule_button, grades_button)
    else:
        keyboard.add(schedule_button)

    bot.send_message(message.chat.id, "Выберите действие:", reply_markup=keyboard)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    with app.app_context():
        student = get_student_by_telegram_id(message.from_user.id)
        if student:
            bot.reply_to(message, f"Добро пожаловать, {student.first_name} {student.last_name}!")
            send_schedule_button(message, student.group_id, student.id)
            return

    # ... (остальной код без изменений) ...

def start_bot():
    bot.polling()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    start_bot()