import html
from telebot import types
from database.models import User, User_info, Authorized_users, Admin, Content
from database.session import SessionLocal
from database.content_session import ContentSessionLocal

def search(bot, call):
    db = SessionLocal()
    section = 'search_emp'
    if (db.query(Admin).filter(call.from_user.id == Admin.auth_token).first()):
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(types.InlineKeyboardButton(f"Изменить текст", callback_data=f'edit_section:{section}:search_emp'))
        markup.add(types.InlineKeyboardButton("Назад", callback_data="back_to_main"))
    else:
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(types.InlineKeyboardButton("Назад", callback_data="back_to_main"))
    db = ContentSessionLocal()
    content = db.query(Content).filter(Content.section == section).first()
    bot.send_message(call.message.chat.id, f"📌 {content.title}\n{content.text}", reply_markup=markup)
    
    bot.register_next_step_handler(call.message, search_by_fio, bot)

# Глобальный словарь для хранения последнего поискового запроса пользователя
user_search_cache = {}

def search_by_fio(message, bot):
    try:
        query = message.text.strip()
        if not query:
            bot.send_message(message.chat.id, "Введите запрос.")
            return

        search_parts = [part.lower() for part in query.split() if part]
        db = SessionLocal()
        users = db.query(User_info).all()

        matched_users = [
            user for user in users
            if user.full_name and all(part in user.full_name.lower() for part in search_parts)
        ]
        matched_users.sort(key=lambda u: sum(part in u.full_name.lower() for part in search_parts), reverse=True)

        if not matched_users:
            bot.send_message(message.chat.id, "Не найдено.")
            return

        # Сохраняем ID в порядке релевантности
        user_search_cache[message.from_user.id] = {
            'results': [u.id for u in matched_users]
        }

        # Отправляем первую страницу
        send_users_paginated_cached(
            bot=bot,
            call_or_message=message,  # ← message, is_new_message=True по умолчанию
            users=matched_users,
            page=0,
            is_new_message=True
        )

    except Exception as e:
        bot.send_message(message.chat.id, "Ошибка при поиске.")
        print(f"Error: {e}")
    finally:
        db.close()


def send_users_paginated_cached(bot, call_or_message, users, page=0, user_id=None, is_new_message=True):
    """
    Отправляет или редактирует сообщение с пагинацией.
    :param call_or_message: может быть message (при первом вызове) или call (при редактировании)
    :param users: список User_info
    :param page: номер страницы
    :param user_id: ID пользователя (для кэша)
    :param is_new_message: флаг, новое ли это сообщение
    """
    PAGE_SIZE = 5
    total_pages = (len(users) + PAGE_SIZE - 1) // PAGE_SIZE
    start_idx = page * PAGE_SIZE
    end_idx = start_idx + PAGE_SIZE
    page_users = users[start_idx:end_idx]

    markup = types.InlineKeyboardMarkup(row_width=3)

    # Кнопки навигации
    buttons = []

    if page > 0:
        buttons.append(types.InlineKeyboardButton("⬅️ Назад", callback_data=f"emp_page:{page - 1}"))

    if end_idx < len(users):
        buttons.append(types.InlineKeyboardButton("➡️ Ещё", callback_data=f"emp_page:{page + 1}"))

    # Добавляем кнопки сотрудников
    for user in page_users:
        markup.add(
            types.InlineKeyboardButton(
                user.full_name or "Без имени",
                callback_data=f"emp_detail:{user.id}"
            )
        )

    # Добавляем навигацию вниз
    if buttons:
        markup.row(*buttons)
    else:
        # Если больше нет страниц — просто "Закрыть" или "Назад в меню"
        markup.add(types.InlineKeyboardButton("🔙 Назад в меню", callback_data="back_to_main"))

    text = f"Результаты поиска (страница {page + 1}/{total_pages}):"

    # Определяем, куда отправлять
    if is_new_message:
        bot.send_message(call_or_message.chat.id, text, reply_markup=markup)
    else:
        try:
            bot.edit_message_text(
                chat_id=call_or_message.message.chat.id,
                message_id=call_or_message.message.message_id,
                text=text,
                reply_markup=markup
            )
        except:
            # Если не удалось отредактировать (например, текст не изменился)
            pass



def handle_employee_page(call, bot):
    try:
        page = int(call.data.split(":")[1])
        user_id = call.from_user.id

        if user_id not in user_search_cache:
            bot.answer_callback_query(call.id, "Сессия поиска истекла.")
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text="Сессия поиска истекла. Пожалуйста, начните поиск заново.",
                reply_markup=types.InlineKeyboardMarkup().add(
                    types.InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")
                )
            )
            return

        # Получаем сохранённые ID пользователей
        result_ids = user_search_cache[user_id]['results']
        db = SessionLocal()
        users = db.query(User_info).filter(User_info.id.in_(result_ids)).all()

        # Восстанавливаем порядок
        id_to_user = {u.id: u for u in users}
        matched_users = [id_to_user[uid] for uid in result_ids if uid in id_to_user]

        # Редактируем сообщение с новой страницей

        send_users_paginated_cached(
            bot=bot,
            call_or_message=call,
            users=matched_users,
            page=page,
            user_id=user_id,
            is_new_message=False
        )

        bot.answer_callback_query(call.id)
    except Exception as e:
        bot.send_message(call.message.chat.id, "Ошибка при переключении страницы.")
        print(f"Error in emp_page: {e}")
    finally:
        db.close()

def handle_employee_detail(call, bot):
    try:
        # Парсим ID из колбэка: emp_detail:<user_info_id>
        user_info_id = int(call.data.split(":")[1])
        db = SessionLocal()

        # Получаем данные сотрудника из User_info (таблица about_users)
        user_info = db.query(User_info).filter(User_info.id == user_info_id).first()
        if not user_info:
            bot.answer_callback_query(call.id, "❌ Данные сотрудника не найдены.")
            return

        # Получаем связанный User по id (не user_id!)
        user = db.query(User).filter(User.id == user_info.id).first()

        # Формируем текст
        full_name = user_info.full_name or "Не указано"
        #position = user_info.position or "Не указана"
        office = user_info.office or "Не указан"
        phone = user_info.officephone or "Не указан"
        email = user_info.mail or "Не указан"  # поле mail в about_users
        telegram = f"@{user_info.username}" if user_info.username else "Не указан"

        details = (
            f"👤 <b>ФИО:</b> {html.escape(full_name or 'Не указано')}\n"
            f"🏢 <b>Офис:</b> {html.escape(office or 'Не указан')}\n"
            f"📞 <b>Телефон:</b> {html.escape(phone or 'Не указан')}\n"
            f"✉️ <b>Email:</b> {html.escape(email or 'Не указан')}\n"
            f"👤 <b>Telegram:</b> {html.escape(telegram or 'Не указан')}"
        )


        # Кнопка "Назад к результатам"
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton("⬅️ Назад к результатам", callback_data="back_to_results")
        )

        # Редактируем сообщение
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=details,
            reply_markup=markup,
            parse_mode="HTML"
        )

        bot.answer_callback_query(call.id)

    except Exception as e:
        bot.send_message(call.message.chat.id, "Ошибка при отображении данных сотрудника.")
        print(f"Error in handle_employee_detail: {e}")
    finally:
        db.close()

def handle_back_to_results(call, bot):
    try:
        user_id = call.from_user.id

        if user_id not in user_search_cache:
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text="Сессия поиска истекла.",
                reply_markup=types.InlineKeyboardMarkup().add(
                    types.InlineKeyboardButton("🔙 В меню", callback_data="back_to_main")
                )
            )
            return

        # Восстанавливаем список найденных сотрудников
        result_ids = user_search_cache[user_id]['results']
        db = SessionLocal()
        users = db.query(User_info).filter(User_info.id.in_(result_ids)).all()

        id_to_user = {u.id: u for u in users}
        matched_users = [id_to_user[uid] for uid in result_ids if uid in id_to_user]

        # Показываем первую страницу результатов
        from handlers.search_emp_handler import send_users_paginated_cached
        send_users_paginated_cached(
            bot=bot,
            call_or_message=call,
            users=matched_users,
            page=0,
            is_new_message=False
        )

        bot.answer_callback_query(call.id)

    except Exception as e:
        bot.send_message(call.message.chat.id, "Ошибка при возврате к результатам.")
        print(f"Error in handle_back_to_results: {e}")
    finally:
        db.close()