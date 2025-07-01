from main import start, loop
import telebot
from dotenv import load_dotenv
import os

load_dotenv()
API_TOKEN = os.getenv("API_TOKEN")


bot = telebot.TeleBot(API_TOKEN)

start(bot)
loop(bot)

bot.infinity_polling()