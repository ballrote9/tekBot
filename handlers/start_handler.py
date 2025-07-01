from telebot.types import Message

def register_start_handler(bot):
    @bot.message_handler(commands=["start"])
    def start(message: Message):
        bot.send_message(message.chat.id, "Привет! Я твой бот.")
