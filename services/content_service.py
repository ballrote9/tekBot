from database.content_session import ContentSessionLocal
from database.models import Content, ContentFile
import os

from services.auth_check import check_auth

def update_content(section: str, title: str = None, text: str = None):
    db = ContentSessionLocal()
    try:
        content = db.query(Content).filter(Content.section == section).first()
        if not content:
            content = Content(section=section, title=title, text=text)
            db.add(content)
        else:
            if title:
                content.title = title
            if text:
                content.text = text
        db.commit()
        db.refresh(content)
        return content
    finally:
        db.close()


def add_file_to_content(section: str, file_path: str):
    db = ContentSessionLocal()
    try:
        content = db.query(Content).filter(Content.section == section).first()
        if not content:
            content = Content(section=section)
            db.add(content)
            db.commit()

        new_file = ContentFile(file_path=file_path, content=content)
        db.add(new_file)
        db.commit()
        db.refresh(new_file)
        return new_file
    finally:
        db.close()

def get_content_files(section: str):
    db = ContentSessionLocal()
    try:
        content = db.query(Content).filter(Content.section == section).first()
        if content:
            return content.files
        return []
    finally:
        db.close()

def delete_content_file(file_id: int):
    db = ContentSessionLocal()
    try:
        file_record = db.query(ContentFile).get(file_id)
        if file_record:
            file_path = file_record.file_path
            db.delete(file_record)
            db.commit()

            # Опционально: удалить физически файл с диска
            if os.path.exists(file_path):
                os.remove(file_path)

            return True
        return False
    except Exception as e:
        db.rollback()
        print(f"[ERROR] Не удалось удалить файл: {e}")
        return False
    finally:
        db.close()


def show_content(bot, call, markup):
    
    if not check_auth(bot, call): 
        return
    
    section = call.data
    db = ContentSessionLocal()
    try:
        content = db.query(Content).filter(Content.section == section).first()
        if content:
            bot.send_message(call.message.chat.id, f"📌 {content.title}\n\n{content.text}",
                             reply_markup = markup)

            for file in content.files:
                if os.path.exists(file.file_path):
                    with open(file.file_path, "rb") as f:
                        bot.send_document(call.message.chat.id, f)
                else:
                    bot.send_message(call.message.chat.id, f"Файл {file.file_path} не найден.")
        else:
            bot.send_message(call.message.chat.id, "Информация пока недоступна.")
    finally:
        db.close()