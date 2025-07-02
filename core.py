from handlers.start_handler import register_start_handler
from handlers.menu_handler import register_menu_handlers
import telebot
from dotenv import load_dotenv
import os

load_dotenv()
API_TOKEN = os.getenv("API_TOKEN")


bot = telebot.TeleBot(API_TOKEN)

register_start_handler(bot)
register_menu_handlers(bot)

bot.infinity_polling()