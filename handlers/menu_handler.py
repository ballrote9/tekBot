from telebot import types

def register_menu_handlers(bot):
    @bot.callback_query_handler(func=lambda call: True)
    def handle_callback(call):
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
        elif call.data == "back_to_main":
            from handlers.start_handler import send_welcome
            send_welcome(call.message)