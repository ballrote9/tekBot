from telebot import types
import hashlib
from database.models import User, User_info, Authorized_users, Admin
from database.session import SessionLocal


def show_main_menu(bot, message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    buttons = [
        types.InlineKeyboardButton("Информация о компании", callback_data="info"),
        types.InlineKeyboardButton("Информация для сотрудников", callback_data="training"),
        types.InlineKeyboardButton("FAQ", callback_data="faq"),
        types.InlineKeyboardButton("Обратная связь", callback_data="feedback"),
        types.InlineKeyboardButton("Поддержка", callback_data="support")
    ]
    db = SessionLocal()
    if (db.query(Admin).filter(message.from_user.id == Admin.auth_token)):
        buttons.append(types.InlineKeyboardButton("Изменить", callback_data='change_data'))
    markup.add(*buttons)
    bot.send_message(
        message.chat.id,
        "👋 Привет! Я ваш помощник по онбордингу.\n"
        "Выберите интересующий раздел:",
        reply_markup=markup
    )

# --- Регистрация обработчиков ---
def register_start_handler(bot):
    # Авторизация Пользователей
    def handle_password(message, sent=None):
        entered_password = message.text.strip()
        hashed_password = hashlib.sha256(entered_password.encode()).hexdigest()
        telegram_id = message.from_user.id
        found = False
        db = SessionLocal()

        # Ищем пользователя среди уже авторизованных для избежания повторного входа по чужому паролю
        auth_user = db.query(Authorized_users).filter(Authorized_users.auth_token == telegram_id).first()
        if auth_user:
            if hashed_password == auth_user.user.hash_pass:
                found = True
                user = auth_user.user
            else: 
                bot.delete_message(message.chat.id, sent.message_id)
                bot.delete_message(message.chat.id, message.message_id)
                sent = bot.send_message(message.chat.id, "Неверный пароль.\r\nПопробуйте еще раз!")
            
                bot.register_next_step_handler(message, handle_password, sent)
                return
        # Поиск пользователя среди всех юзеров
        if not found:
            user_entry = db.query(User)
            for user in user_entry:
                if hashed_password == user.hash_pass and not user.is_authorized:
                    found = True
                    break

        if not found:
            bot.delete_message(message.chat.id, sent.message_id)
            bot.delete_message(message.chat.id, message.message_id)
            sent = bot.send_message(message.chat.id, "Неверный пароль.\r\nПопробуйте еще раз!")
            
            bot.register_next_step_handler(message, handle_password, sent)
            return
        

        # Обновляем auth_token на telegram_id в обеих таблицах
        if not user.is_authorized:
            user_info = user.user_info
            user_info.auth_token = str(telegram_id)
            user.auth_token = str(telegram_id)
            user.is_authorized = True
            db.add(Authorized_users(
                auth_token = user.auth_token
            ))
            db.commit()

            bot.delete_message(message.chat.id, sent.message_id)
            bot.delete_message(message.chat.id, message.message_id)
            bot.send_message(message.chat.id, f"Вы успешно авторизованы, {user_info.full_name}!")

        else:
            bot.delete_message(message.chat.id, sent.message_id)
            bot.delete_message(message.chat.id, message.message_id)
            bot.send_message(message.chat.id, f"Вы успешно авторизованы, {user.user_info.full_name}!")
        db.close()

    
    @bot.message_handler(commands=["start"])
    def send_welcome(message):
        sent = bot.send_message(
            message.chat.id,
            "Введите пароль:"
        )
        bot.register_next_step_handler(message, handle_password, sent)
    
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
        
    def greetings(message):
        bot.send_message(
            message.chat.id,
            "'Краткое описание основных функций бота'"
        )
        bot.send_message(
            message.chat.id,
            "Инструкция по дальнейшему взаимодействию (например, \"Чтобы получить информацию о компании, нажмите кнопку 'Информация'\")."
        )