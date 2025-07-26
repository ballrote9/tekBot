from database.models import Authorized_users, Admin
from database.session import SessionLocal

def is_user_authorized(user_id: int):
    db = SessionLocal()
    try:
        uid = str(user_id)  # Конвертируем в строку для поиска
        is_authorized = (
            db.query(Authorized_users).filter(Authorized_users.auth_token == uid).first() is not None or
            db.query(Admin).filter(Admin.auth_token == uid).first() is not None
        )
        print(f"[AUTH DEBUG] User id: {uid}, Authorized: {is_authorized}")
        return is_authorized
    except Exception as e:
        print(f"[AUTH ERROR] {e}")
        return False
    finally:
        db.close()

def get_user_id_from_message(message):
    """Получает правильный user_id из сообщения"""
    # Для callback query
    if hasattr(message, 'from_user') and message.from_user:
        return message.from_user.id
    
    # Для вложенного сообщения в callback
    if hasattr(message, 'message') and hasattr(message.message, 'from_user'):
        return message.message.from_user.id
    
    # Для edited_message и других случаев
    if hasattr(message, 'edited_message') and hasattr(message.edited_message, 'from_user'):
        return message.edited_message.from_user.id
    
    return None

def check_auth(bot, message):
    user_id = get_user_id_from_message(message)
    
    if user_id is None:
        print("[AUTH ERROR] Cannot determine user ID")
        bot.reply_to(message, "⛔ Ошибка авторизации.")
        return False
    
    print(f"[AUTH] Checking user ID: {user_id}")
    
    if not is_user_authorized(user_id):
        bot.reply_to(message, "⛔ Доступ запрещен.")
        return False
    return True

def require_auth(bot):
    def decorator(func):
        def wrapper(message, *args, **kwargs):
            user_id = get_user_id_from_message(message)
            
            if user_id is None:
                print("[AUTH DECORATOR] Cannot determine user ID")
                if hasattr(message, 'id'):  # callback query
                    bot.answer_callback_query(message.id, "⛔ Ошибка авторизации")
                else:
                    bot.reply_to(message, "⛔ Ошибка авторизации.")
                return
            
            print(f"[AUTH DECORATOR] Checking user ID: {user_id}")
            
            if not is_user_authorized(user_id):
                if hasattr(message, 'id'):  # Это callback query
                    bot.answer_callback_query(message.id, "⛔ Доступ запрещен")
                else:  # Это обычное сообщение
                    bot.reply_to(message, "⛔ Доступ запрещен. Пожалуйста, авторизуйтесь через /start")
                return
            return func(message, *args, **kwargs)
        return wrapper
    return decorator