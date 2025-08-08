# handlers/upload_emp_handler.py

import os
import pandas as pd
import hashlib
import secrets
import datetime
from database.models import User, User_info
from database.session import SessionLocal  # Твоя сессия
from telebot import TeleBot
from telebot.types import CallbackQuery, Message
import openpyxl  # Для записи Excel

# Путь к файлу с паролями
PASSWORDS_FILE = "data/user_pass.xlsx"

# --- Генерация пароля ---
def generate_password(length=8):
    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

# --- Генерация auth_token ---
def generate_auth_token():
    return secrets.token_urlsafe(64)[:64]  # Ровно 64 символа

# --- Хеширование пароля ---
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

# --- FSM: ожидание файла ---
waiting_for_excel = {}  # user_id → True, если ожидается файл

# --- Функция: сохранить пароли в Excel ---
def save_passwords_to_excel(passwords_list):
    os.makedirs("data", exist_ok=True)
    df_existing = pd.DataFrame()
    if os.path.exists(PASSWORDS_FILE):
        df_existing = pd.read_excel(PASSWORDS_FILE)

    # Преобразуем новый список в DataFrame
    df_new = pd.DataFrame(passwords_list)

    # Объединяем: заменяем строки с теми же email, добавляем новые
    if not df_existing.empty:
        df_combined = df_existing.set_index("mail")
        df_new = df_new.set_index("mail")
        df_combined.update(df_new)
        df_combined = pd.concat([
            df_new[~df_new.index.isin(df_combined.index)],
            df_combined
        ])
        df_combined = df_combined.reset_index()
    else:
        df_combined = df_new.reset_index(drop=True)

    # Сохраняем
    df_combined.to_excel(PASSWORDS_FILE, index=False)
    return PASSWORDS_FILE


# --- Регистрация обработчиков ---
def register_handlers(bot: TeleBot):
    @bot.callback_query_handler(func=lambda call: call.data == "upload_staff")
    def upload_staff_handler(call: CallbackQuery):
        bot.send_message(
            call.message.chat.id,
            "📤 Отправьте Excel-файл с информацией о сотрудниках.\n"
            "Ожидаемые столбцы: `name`, `mail`, `office`, `officephone`."
        )
        waiting_for_excel[call.from_user.id] = True
        bot.answer_callback_query(call.id)

    @bot.message_handler(content_types=['document'], func=lambda m: m.from_user.id in waiting_for_excel)
    def handle_excel_file(message: Message):
        user_id = message.from_user.id
        if not waiting_for_excel.get(user_id):
            return

        # Убираем флаг
        del waiting_for_excel[user_id]

        file_info = bot.get_file(message.document.file_id)
        file_name = message.document.file_name

        if not file_name.endswith(('.xlsx', '.xls')):
            bot.send_message(message.chat.id, "❌ Ожидался файл Excel (.xlsx или .xls).")
            return

        # Скачиваем файл
        downloaded = bot.download_file(file_info.file_path)
        temp_path = f"temp_upload_{user_id}.xlsx"
        with open(temp_path, 'wb') as f:
            f.write(downloaded)

        session = SessionLocal()
        new_credentials = []  # Для сохранения в Excel: mail, password

        try:
            df = pd.read_excel(temp_path)
            required = {'name', 'mail', 'office', 'officephone'}
            if not required.issubset(df.columns):
                bot.send_message(message.chat.id,
                                 f"❌ Не хватает столбцов. Нужны: {required}\n"
                                 f"В файле: {list(df.columns)}")
                os.remove(temp_path)
                return

            # Очистка данных
            df['mail'] = df['mail'].astype(str).str.strip().str.lower()
            df = df.dropna(subset=['mail'])
            df = df[df['mail'] != 'nan']
            df = df.drop_duplicates(subset='mail', keep='first')

            # Все текущие пользователи из БД
            existing_users = session.query(User_info).all()
            existing_map = {u.mail.lower(): u for u in existing_users if u.mail}

            added = 0
            updated = 0
            deleted = 0

            # --- 1. Обработка файла ---
            for _, row in df.iterrows():
                mail = row['mail']
                name = str(row['name']).strip()
                office = str(row['office']).strip() if pd.notna(row['office']) else None
                officephone = str(row['officephone']).strip() if pd.notna(row['officephone']) else None

                if mail in existing_map:
                    # Обновляем
                    user_info = existing_map[mail]
                    user = session.query(User).filter(User.auth_token == user_info.auth_token).first()

                    user_info.full_name = name
                    user_info.office = office
                    user_info.officephone = officephone
                    user_info.mail = mail

                    if user:
                        user.last_activity = datetime.datetime.now()

                    session.add(user_info)
                    session.add(user)
                    updated += 1

                    del existing_map[mail]  # Убираем из "удаляемых"

                else:
                    # Добавляем нового
                    auth_token = generate_auth_token()
                    password = generate_password()
                    hashed = hash_password(password)

                    # Создаём User
                    new_user = User(
                        auth_token=auth_token,
                        hash_pass=hashed,
                        is_authorized=False,
                        created_at=datetime.datetime.now(),
                        last_activity=datetime.datetime.now()
                    )
                    session.add(new_user)

                    # Создаём User_info
                    new_user_info = User_info(
                        auth_token=auth_token,
                        full_name=name,
                        mail=mail,
                        office=office,
                        officephone=officephone
                    )
                    session.add(new_user_info)

                    session.flush()  # Чтобы получить ID, если нужно

                    # Сохраняем пароль для экспорта
                    new_credentials.append({
                        "full_name": name,
                        "mail": mail,
                        "password": password,
                        "auth_token": auth_token
                    })

                    added += 1

            # --- 2. Удаление уволенных ---
            for user_info in existing_map.values():
                session.query(User).filter(User.auth_token == user_info.auth_token).delete()
                session.delete(user_info)
                deleted += 1

            session.commit()

            # --- 3. Сохраняем пароли в Excel ---
            if new_credentials:
                save_passwords_to_excel(new_credentials)
                # Отправляем файл с паролями
                with open(PASSWORDS_FILE, 'rb') as f:
                    bot.send_document(
                        message.chat.id,
                        f,
                        caption="🔐 Новые и обновлённые пароли сохранены."
                    )
            else:
                bot.send_message(message.chat.id, "🔐 Новых паролей не было сгенерировано.")

            # --- Ответ ---
            bot.send_message(
                message.chat.id,
                f"✅ Обработка завершена:\n"
                f"➕ Добавлено: {added}\n"
                f"🔄 Обновлено: {updated}\n"
                f"🗑 Удалено (уволенные): {deleted}"
            )

        except Exception as e:
            session.rollback()
            bot.send_message(message.chat.id, f"❌ Ошибка: {str(e)}")
            print(f"Error: {e}")
        finally:
            session.close()
            if os.path.exists(temp_path):
                os.remove(temp_path)