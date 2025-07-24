from database.models import Content, ContentFile
from database.content_session import ContentSessionLocal, ContentBase, content_engine


    # Создаёт все таблицы в БД, если они ещё не созданы
def create_tables():
    try:
        ContentBase.metadata.create_all(bind=content_engine)
        print("[OK] Таблицы успешно созданы или уже существуют")
    except Exception as e:
        print(f"[ERROR] Не удалось создать таблицы: {e}")
        raise


    # Добавляет стандартные разделы и опциональные файлы
def add_default_content(db: ContentSessionLocal):
    content_data = [
        {
            "section": "history",
            "title": "История компании",
            "text": "Это информация о истории компании ТЭК",
            "files": ["data/company_info/history.pdf"]
        },
        {
            "section": "values",
            "title": "Наши ценности",
            "text": "Это ценности компании ТЭК",
            "files": ["data/company_info/values.pdf"]
        }
    ]

    for item in content_data:
        existing = db.query(Content).filter(Content.section == item["section"]).first()
        if not existing:
            # Создаём новый раздел
            new_content = Content(
                section=item["section"],
                title=item["title"],
                text=item["text"]
            )
            db.add(new_content)
            db.flush()  # Чтобы получить ID перед добавлением файлов

            # Добавляем файлы, если указаны
            for file_path in item.get("files", []):
                db.add(ContentFile(content=new_content, file_path=file_path))

    try:
        db.commit()
        print("[INFO] Стандартный контент и файлы добавлены")
    except Exception as e:
        db.rollback()
        print(f"[ERROR] Ошибка при добавлении контента: {e}")
        raise


if __name__ == "__main__":
    create_tables()
    db = ContentSessionLocal()
    # Eсли есть какое-нибудь наполнение, можно добавить
    # через функцию add_default_content(db)
    """ try:
        add_default_content(db)
    finally:
        db.close() """