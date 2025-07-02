from telebot import types

def show_faq(bot, message):
    markup = types.InlineKeyboardMarkup(row_width=1)

    buttons = [
        types.InlineKeyboardButton("Как пройти онбординг?", callback_data="faq_onboarding"),
        types.InlineKeyboardButton("Как получить доступ к материалам?", callback_data="faq_materials"),
        types.InlineKeyboardButton("Как записаться на экскурсию?", callback_data="faq_tours"),
        types.InlineKeyboardButton("⬅ Назад", callback_data="back_to_main")
    ]

    markup.add(*buttons)

    bot.send_message(
        message.chat.id,
        "❓ Часто задаваемые вопросы:\n"
        "Выберите интересующий вопрос.",
        reply_markup=markup
    )