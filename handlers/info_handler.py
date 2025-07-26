from telebot import types
from database.session import SessionLocal
from database.content_session import ContentSessionLocal
from database.models import Admin, Content
import os

from services.auth_check import require_auth
from services.content_service import show_content


    # Функция вывода меню для пункта "информация о компании" основного меню
def register_about_company_menu_handler(bot):
    # Ловит колбеки, если они из списка колбеков кнопок из подменю "Информация о компании"
    @bot.callback_query_handler(func=lambda call: call.data in ["history", "values", "info"])
    @require_auth(bot)
    def callback_handler(call):
        markup = types.InlineKeyboardMarkup(row_width=1)
        buttons = []
        db = SessionLocal()
        if (db.query(Admin).filter(call.from_user.id == Admin.auth_token).first()):
            buttons.append(types.InlineKeyboardButton(f"Изменить", callback_data=f'edit_section:{call.data}:training'))
            buttons.append(types.InlineKeyboardButton(f"Назад", callback_data='training'))
        markup.add(*buttons)

        if call.data == "info":
            markup = types.InlineKeyboardMarkup(row_width=1)
            buttons = [
                types.InlineKeyboardButton("История компании", callback_data="history"),
                types.InlineKeyboardButton("Ценности", callback_data="values"),
                types.InlineKeyboardButton("⬅ Назад", callback_data="back_to_main")
            ]
           
            markup.add(*buttons)

            bot.send_message(
                call.message.chat.id,
                "📚 Здесь вы найдете информацию о нашей компании.",
                reply_markup=markup
            )
        else:
            show_content(bot, call, markup)
    