from telebot import types


def register_start_handler(bot):
    @bot.message_handler(commands=["start"])
    def start(message: types.Message):
        
        """ markup = types.ReplyKeyboardMarkup()
        btn1 = types.KeyboardButton('Информация о компании ТЭК')
        markup.row(btn1)
        btn2 = types.KeyboardButton('Экскурсии по компании')
        markup.row(btn2)
        btn3 = types.KeyboardButton('Виртуальная экскрусия по компании')
        markup.row(btn3)
        btn4 = types.KeyboardButton('Организационная структура компании')
        markup.row(btn4)
        btn5 = types.KeyboardButton('Столовая')
        #markup.row(btn5)
        btn6 = types.KeyboardButton('Корпоративные мероприятия')
        markup.row(btn5, btn6)
        btn7 = types.KeyboardButton('Обучающие материалы')
        markup.row(btn7)
        btn8 = types.KeyboardButton('Часто задаваемые вопросы (FAQ)')
        markup.row(btn8)
        btn9 = types.KeyboardButton('Оформление документов')
        markup.row(btn9)
        btn10 = types.KeyboardButton('Обратная связь')
        markup.row(btn10)
        btn11 = types.KeyboardButton('Поддержка и помощь')
        markup.row(btn11)
        bot.send_message(message.chat.id, "Привет! Я твой бот.", reply_markup = markup) """



        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton('Информация о компании ТЭК', callback_data="info")
        markup.row(btn1)
        btn2 = types.InlineKeyboardButton('Экскурсии по компании', callback_data="что-то")
        markup.row(btn2)
        btn3 = types.InlineKeyboardButton('Виртуальная экскрусия по компании', callback_data="что-то")
        markup.row(btn3)
        btn4 = types.InlineKeyboardButton('Организационная структура компании', callback_data="что-то")
        markup.row(btn4)
        btn5 = types.InlineKeyboardButton('Столовая', callback_data="что-то")
        #markup.row(btn5)
        btn6 = types.InlineKeyboardButton('Корпоративные мероприятия', callback_data="что-то")
        markup.row(btn5, btn6)
        btn7 = types.InlineKeyboardButton('Обучающие материалы', callback_data="что-то")
        markup.row(btn7)
        btn8 = types.InlineKeyboardButton('Часто задаваемые вопросы (FAQ)', callback_data="что-то")
        markup.row(btn8)
        btn9 = types.InlineKeyboardButton('Оформление документов', callback_data="что-то")
        markup.row(btn9)
        btn10 = types.InlineKeyboardButton('Обратная связь', callback_data="что-то")
        markup.row(btn10)
        btn11 = types.InlineKeyboardButton('Поддержка и помощь', callback_data="что-то")
        markup.row(btn11)
        bot.send_message(message.chat.id, "Привет! Я твой бот.", reply_markup = markup) 

    @bot.callback_query_handler(func = lambda callback: True)
    def callback_nav(callback):
        match callback.data:
            case 'info':
                markup = types.ReplyKeyboardMarkup()
                btn1 = types.KeyboardButton('Информация о компании ТЭК')
                markup.row(btn1)
                btn2 = types.KeyboardButton('Экскурсии по компании')
                markup.row(btn2)
                bot.send_message(callback.message.chat.id, "Навигация", reply_markup = markup)
