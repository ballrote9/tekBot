# init_content.py
from database.content_session import ContentSessionLocal
from database.models import Content
from services.sections import SECTIONS

def initialize_content():
    db = ContentSessionLocal()
    try:
        for section_key, section_data in SECTIONS.items():
            # Проверяем, существует ли уже такой контент
            existing_content = db.query(Content).filter(Content.section == section_key).first()
            
            if not existing_content:
                # Создаем новый контент
                content = Content(
                    section=section_key,
                    title=section_data.get("title", ""),
                    text=section_data.get("description", "")
                )
                db.add(content)
                print(f"Добавлен контент для раздела: {section_key}")
            else:
                # Обновляем существующий контент
                existing_content.title = section_data.get("title", existing_content.title)
                existing_content.text = section_data.get("description", existing_content.text)
                print(f"Обновлен контент для раздела: {section_key}")
        
        db.commit()
        print("✅ Все разделы успешно добавлены/обновлены в базе данных")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Ошибка при инициализации контента: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    initialize_content()