from telebot import types

def show_employee_info_menu(bot, message):
    markup = types.InlineKeyboardMarkup(row_width=1)

    buttons = [
        types.InlineKeyboardButton("Обучающие материалы", callback_data="training_materials"),
        types.InlineKeyboardButton("Экскурсии по компании", callback_data="company_tours"),
        types.InlineKeyboardButton("Виртуальная экскурсия", callback_data="virtual_tour"),
        types.InlineKeyboardButton("Организационная структура", callback_data="org_structure"),
        types.InlineKeyboardButton("Столовая", callback_data="canteen"),
        types.InlineKeyboardButton("Корпоративные мероприятия", callback_data="corporate_events"),
        types.InlineKeyboardButton("Оформление документов", callback_data="document_filling"),
        types.InlineKeyboardButton("⬅ Назад", callback_data="back_to_main")
    ]

    markup.add(*buttons)

    bot.send_message(
        message.chat.id,
        "🎓 Информация для сотрудников:\n"
        "Выберите нужный раздел.",
        reply_markup=markup
    )