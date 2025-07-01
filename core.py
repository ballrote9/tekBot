from handlers.start_handler import register_start_handler
import telebot
from dotenv import load_dotenv
import os

load_dotenv()
API_TOKEN = os.getenv("API_TOKEN")


bot = telebot.TeleBot(API_TOKEN)

register_start_handler(bot)

bot.infinity_polling()