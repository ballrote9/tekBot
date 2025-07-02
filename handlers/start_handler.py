from telebot import types


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
        #init_db()  # Инициализируем БД при старте
        show_main_menu(bot, message)

    @bot.message_handler(commands=["menu"])
    def show_menu(message):
        show_main_menu(bot, message)