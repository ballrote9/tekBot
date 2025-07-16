from telebot import types
from database.models import Content
from database.session import SessionLocal
import os

def register_menu_handlers(bot):
    @bot.callback_query_handler(func=lambda call: True)
    def handle_callback(call):
        # --- Главное меню ---
        if call.data == "info":
            from handlers.info_handler import show_info_menu
            show_info_menu(bot, call.message)
        elif call.data == "training":
            from handlers.emp_info_handler import show_employee_info_menu
            show_employee_info_menu(bot, call.message)
        elif call.data == "faq":
            from handlers.faq_handler import show_faq
            show_faq(bot, call.message)
        elif call.data == "feedback":
            from handlers.feedback_handler import ask_feedback
            ask_feedback(bot, call.message)
        elif call.data == "support":
            from handlers.support_handler import show_support
            show_support(bot, call.message)

        # --- Подменю "Информация о компании" ---
        elif call.data == "history":
            db = SessionLocal()
            content = db.query(Content).filter(Content.section == "history").first()
            if content:
                bot.send_message(call.message.chat.id, f"📌 {content.title}\n\n{content.text}")
                if content.file_path and os.path.exists(content.file_path):
                    with open(content.file_path, "rb") as f:
                        bot.send_document(call.message.chat.id, f)
            else:
                bot.send_message(call.message.chat.id, "Информация пока недоступна.")
            db.close()

        elif call.data == "values":
            db = SessionLocal()
            content = db.query(Content).filter(Content.section == "values").first()
            if content:
                bot.send_message(call.message.chat.id, f"💎 {content.title}\n\n{content.text}")
                if content.file_path and os.path.exists(content.file_path):
                    with open(content.file_path, "rb") as f:
                        bot.send_document(call.message.chat.id, f)
            else:
                bot.send_message(call.message.chat.id, "Информация пока недоступна.")
            db.close()

        # --- Подменю "Информация для сотрудников" ---
        elif call.data == "training_materials":
            from handlers.emp_info_handler import show_training_materials
            show_training_materials(bot, call.message)

        elif call.data == "company_tours":
            from handlers.emp_info_handler import show_company_tours
            show_company_tours(bot, call.message)

        elif call.data == "virtual_tour":
            from handlers.emp_info_handler import show_virtual_tour
            show_virtual_tour(bot, call.message)

        elif call.data == "org_structure":
            from handlers.emp_info_handler import show_organizational_structure
            show_organizational_structure(bot, call.message)

        elif call.data == "canteen":
            from handlers.emp_info_handler import show_canteen_info
            show_canteen_info(bot, call.message)

        elif call.data == "corporate_events":
            from handlers.emp_info_handler import show_corporate_events
            show_corporate_events(bot, call.message)

        elif call.data == "document_filling":
            from handlers.emp_info_handler import show_document_filling
            show_document_filling(bot, call.message)

        # --- Кнопка "Назад" ---
        elif call.data == "back_to_main":
            from handlers.start_handler import show_main_menu
            show_main_menu(bot, call.message)

        else:
            bot.answer_callback_query(call.id, "Функция пока не реализована")