import telebot
from telebot.types import BotCommand
from dotenv import load_dotenv
import os

from handlers.start_handler import register_start_handler
from handlers.menu_handler import register_menu_handlers
from handlers.admin_content_callback_handler import register_admin_content_callback_handlers


load_dotenv()
API_TOKEN = os.getenv("API_TOKEN")


bot = telebot.TeleBot(API_TOKEN)

commands = [
    BotCommand("start", "Запустить бота"),
    BotCommand("menu", "Открыть меню"),
    BotCommand("profile", "Персональная информация"),
    BotCommand("greetings", "Приветственное сообщение"),
]

bot.set_my_commands(commands)

register_start_handler(bot)
register_admin_content_callback_handlers(bot)
register_menu_handlers(bot)

bot.infinity_polling()