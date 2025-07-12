from telebot import types
import hashlib
from database.models import User, User_info
from database.session import SessionLocal
from database.helpers import verify_password

def show_main_menu(bot, message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    buttons = [
        types.InlineKeyboardButton("Информация о компании", callback_data="info"),
        types.InlineKeyboardButton("Информация для сотрудников", callback_data="training"),
        types.InlineKeyboardButton("FAQ", callback_data="faq"),
        types.InlineKeyboardButton("Обратная связь", callback_data="feedback"),
        types.InlineKeyboardButton("Поддержка", callback_data="support")
    ]
    markup.add(*buttons)
    bot.send_message(
        message.chat.id,
        "👋 Привет! Я ваш помощник по онбордингу.\n"
        "Выберите интересующий раздел:",
        reply_markup=markup
    )

# --- Регистрация обработчиков ---
def register_start_handler(bot):
    @bot.message_handler(commands=["start"])
    def send_welcome(message):
        bot.send_message(
            message.chat.id,
            "Введите пароль:"
        )
    
    @bot.message_handler(commands=['profile'])
    def profile(message):
        telegram_id = message.from_user.id
        db = SessionLocal()

        user_info = db.query(User_info).filter(User_info.auth_token == str(telegram_id)).first()

        if user_info:
            bot.reply_to(message,
                f"ФИО: {user_info.full_name}\n"
                f"Email: {user_info.mail}\n"
                f"Офис: {user_info.office}")
        else:
            bot.reply_to(message, "Вы не авторизованы.")

        db.close()    

    @bot.message_handler(commands=["menu"])
    def show_menu(message):
        show_main_menu(bot, message)
        
    
def catching_all_masseges(bot):
    @bot.message_handler(func=lambda message: True)
    def handle_password(message):
        entered_password = message.text.strip()
        telegram_id = message.from_user.id
        users_id = None
        db = SessionLocal()

        # Ищем пользователя по паролю
        user_entry = db.query(User)

        found = False
        for user in user_entry:
            if hashlib.sha256(entered_password.encode()).hexdigest() == user.hash_pass:
                found = True
                users_id = user.auth_token
                break

        if not found:
            bot.reply_to(message, "Неверный пароль.")
            return

        # Обновляем auth_token на telegram_id в обеих таблицах
        # db.commit()
        if (telegram_id != users_id):
            user_info = db.query(User_info).filter(User_info.auth_token == user.auth_token).first()
            if user_info:
                user_info.auth_token = str(telegram_id)
                user.auth_token = str(telegram_id)
                db.commit()
                bot.reply_to(message, f"Вы успешно авторизованы, {user_info.full_name}!")
            else:
                bot.reply_to(message, "Ошибка: данные не найдены.")
        else:
            bot.reply_to(message, f"Вы успешно авторизованы, {user_info.full_name}!")
        db.close()
        #Unique error (try/catch)
        
        
