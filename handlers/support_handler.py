from telebot import types
from handlers.admin_content_callback_handler import is_admin
def show_support(bot, call):
    markup = types.InlineKeyboardMarkup(row_width=1)

    buttons = [
        types.InlineKeyboardButton("Связаться с администраторами ", callback_data="contact_admin"),
        types.InlineKeyboardButton("⬅ Назад", callback_data="back_to_main")
    ]
    if (is_admin(call.from_user.id)):
        buttons = [
        types.InlineKeyboardButton("Связаться с администраторами ", callback_data="contact_admin"),
        
        types.InlineKeyboardButton("⬅ Назад", callback_data="back_to_main")
    ]
    else:
        buttons = [
        types.InlineKeyboardButton("Связаться с администраторами ", callback_data="contact_admin"),
        types.InlineKeyboardButton("⬅ Назад", callback_data="back_to_main")
    ]
    markup.add(*buttons)

    bot.send_message(
        call.message.chat.id,
        "📞 Поддержка:\n"
        "Если у вас возникли трудности — вы можете обратиться за помощью.",
        reply_markup=markup
    )