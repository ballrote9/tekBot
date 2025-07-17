from telebot import types
from services.content_service import update_content, add_file_to_content, delete_content_file, get_content_files
import os
from services.sections import SECTIONS


def register_admin_content_callback_handlers(bot):
    @bot.callback_query_handler(func=lambda call: call.data.startswith("edit_section:"))
    def start_edit_section(call):
        section = call.data.split(":", 1)[1]
        info = SECTIONS.get(section)

        if not info:
            bot.answer_callback_query(call.id, "Раздел не найден")
            return

        markup = types.InlineKeyboardMarkup()
        buttons = [
            types.InlineKeyboardButton("✏️ Изменить заголовок", callback_data=f"change_title:{section}"),
            types.InlineKeyboardButton("✏️ Изменить текст", callback_data=f"change_text:{section}"),
        ]
        if info.get("allow_file"):
            buttons.append(types.InlineKeyboardButton("📎 Добавить файл", callback_data=f"add_file:{section}"))
            buttons.append(types.InlineKeyboardButton("🗂 Просмотреть файлы", callback_data=f"view_files:{section}"))

        buttons.append(types.InlineKeyboardButton("⬅ Назад", callback_data="info"))
        markup.add(*buttons)

        bot.send_message(
            chat_id=call.message.chat.id,
            text=f"Выберите действие для «{info['title']}»",
            reply_markup=markup
        )

    @bot.callback_query_handler(func=lambda call: call.data.startswith("view_files:"))
    def show_files_list(call):
        section = call.data.split(":", 1)[1]
        files = get_content_files(section)

        info = SECTIONS[section]
        markup = types.InlineKeyboardMarkup()

        if not files:
            bot.send_message(call.message.chat.id, "Файлы не найдены")
            return

        for file in files:
            btn = types.InlineKeyboardButton(f"🗑 {os.path.basename(file.file_path)}", callback_data=f"delete_file:{file.id}")
            markup.add(btn)

        markup.add(types.InlineKeyboardButton("⬅ Назад", callback_data=f"edit_section:{section}"))
        bot.send_message(call.message.chat.id, f"📎 Файлы в разделе «{info['title']}»:", reply_markup=markup)

    # --- Изменить заголовок ---
    @bot.callback_query_handler(func=lambda call: call.data.startswith("change_title:"))
    def request_new_title(call):
        section = call.data.split(":", 1)[1]
        info = SECTIONS[section]
        msg = bot.send_message(call.message.chat.id, f"Введите новый заголовок для «{info['title']}»")
        bot.register_next_step_handler(msg, process_title, section, info)

    def process_title(message, section, info):
        title = message.text.strip()
        update_content(section=section, title=title)
        bot.send_message(message.chat.id, "✅ Заголовок обновлён")

    # --- Изменить текст ---
    @bot.callback_query_handler(func=lambda call: call.data.startswith("change_text:"))
    def request_new_text(call):
        section = call.data.split(":", 1)[1]
        msg = bot.send_message(call.message.chat.id, "Введите новый текст:")
        bot.register_next_step_handler(msg, process_text, section)

    def process_text(message, section):
        text = message.text.strip()
        update_content(section=section, text=text)
        bot.send_message(message.chat.id, "✅ Текст обновлён")

    # --- Добавить файл ---
    @bot.callback_query_handler(func=lambda call: call.data.startswith("add_file:"))
    def request_new_file(call):
        section = call.data.split(":", 1)[1]
        info = SECTIONS[section]
        msg = bot.send_message(call.message.chat.id, f"Загрузите файл для «{info['title']}»")
        bot.register_next_step_handler(msg, process_file, section)

    def process_file(message, section):
        if message.document:
            os.makedirs(f"data/{section}", exist_ok=True)

            file_info = bot.get_file(message.document.file_id)
            downloaded_file = bot.download_file(file_info.file_path)

            file_name = message.document.file_name
            file_path = f"data/{section}/{file_name}"

            with open(file_path, "wb") as f:
                f.write(downloaded_file)

            add_file_to_content(section=section, file_path=file_path)
            bot.send_message(message.chat.id, "📎 Файл успешно добавлен к разделу")
        else:
            bot.send_message(message.chat.id, "❌ Это не файл")
        
    @bot.callback_query_handler(func=lambda call: call.data.startswith("delete_file:"))
    def delete_file(call):
        file_id = int(call.data.split(":", 1)[1])
        deleted = delete_content_file(file_id)
        if deleted:
            bot.send_message(call.message.chat.id, "✅ Файл успешно удалён")
        else:
            bot.send_message(call.message.chat.id, "❌ Ошибка при удалении файла")

