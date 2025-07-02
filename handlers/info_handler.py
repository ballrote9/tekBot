from telebot import types

def show_info_menu(bot, message):
    markup = types.InlineKeyboardMarkup(row_width=1)

    buttons = [
        types.InlineKeyboardButton("История компании", callback_data="history"),
        types.InlineKeyboardButton("Ценности", callback_data="values"),
        types.InlineKeyboardButton("⬅ Назад", callback_data="back_to_main")
    ]

    markup.add(*buttons)

    bot.send_message(
        message.chat.id,
        "📚 Здесь вы найдете информацию о нашей компании.",
        reply_markup=markup
    )