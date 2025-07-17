from telebot import types
from database.content_session import ContentSessionLocal
from database.session import SessionLocal
from database.models import Admin, Content
import os

def show_employee_info_menu(bot, message):
    markup = types.InlineKeyboardMarkup(row_width=1)

    buttons = [
        types.InlineKeyboardButton("Обучающие материалы", callback_data="training_materials"),
        types.InlineKeyboardButton("Экскурсии по компании", callback_data="company_tours"),
        types.InlineKeyboardButton("Виртуальная экскурсия", callback_data="virtual_tour"),
        types.InlineKeyboardButton("Организационная структура", callback_data="org_structure"),
        types.InlineKeyboardButton("Столовая", callback_data="canteen"),
        types.InlineKeyboardButton("Корпоративные мероприятия", callback_data="corporate_events"),
        types.InlineKeyboardButton("Оформление документов", callback_data="document_filling"),
        types.InlineKeyboardButton("⬅ Назад", callback_data="back_to_main")
    ]

    markup.add(*buttons)

    bot.send_message(
        message.chat.id,
        "🎓 Информация для сотрудников:\n"
        "Выберите нужный раздел.",
        reply_markup=markup
    )

# --- Обработчики для каждого пункта меню ---
def show_training_materials(bot, message):
    bot.send_message(message.chat.id, "📚 Здесь вы найдете обучающие материалы: видео, презентации и тесты.")


def show_company_tours(bot, message):
    bot.send_message(message.chat.id, "🚌 Здесь вы можете узнать о предстоящих экскурсиях по компании.")

def show_virtual_tour(bot, message):
    markup = types.InlineKeyboardMarkup(row_width=1)

    buttons = [
        types.InlineKeyboardButton("⬅ Назад", callback_data="back_to_main")
    ]
    db = SessionLocal()
    if (db.query(Admin).filter(message.from_user.id == Admin.auth_token)):
        buttons.append(types.InlineKeyboardButton(f"Изменить «Виртуальный тур»", callback_data='edit_section:virtual_tour'))

    markup.add(*buttons)
    bot.send_message(message.chat.id, "🌐 Виртуальная экскурсия — возможность познакомиться с компанией онлайн.", reply_markup=markup)
    db = ContentSessionLocal()
    content = db.query(Content).filter(Content.section == "virtual_tour").first()
    if content:
        bot.send_message(message.chat.id, f"💎 {content.title}\n\n{content.text}")
        for file in content.files:
            if os.path.exists(file.file_path):
                with open(file.file_path, "rb") as f:
                    bot.send_document(message.chat.id, f)
    else:
        bot.send_message(message.chat.id, "Информация пока недоступна.")
    db.close()


def show_organizational_structure(bot, message):
    bot.send_message(message.chat.id, "🧱 Организационная структура компании. Вы можете скачать файл или посмотреть схему.")


def show_canteen_info(bot, message):
    bot.send_message(message.chat.id, "🍽️ Информация о столовой: режим работы, меню на день.")


def show_corporate_events(bot, message):
    bot.send_message(message.chat.id, "🎉 Корпоративные мероприятия: Маёвка, TEAM-building и другие события.")

def show_document_filling(bot, message):
    bot.send_message(message.chat.id, "📄 Как оформить документы: отпуск, больничный, справки и т.д.")
