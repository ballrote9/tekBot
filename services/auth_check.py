from database.models import Authorized_users, Admin
from database.session import SessionLocal

    # Проверка является ли юзер админом или авторизованным пользователем 
def is_user_authorized(user_id: int):
    db = SessionLocal()
    uid = str(user_id)
    is_authorized = (
        db.query(Authorized_users).filter(Authorized_users.auth_token == uid).first() or
        db.query(Admin).filter(Admin.auth_token == uid).first()
    )
    db.close()
    print()
    return is_authorized is not None  # Возвращаем boolean, а не объект

    # Функция для проверки авторизации
def check_auth(bot, message):
    # Более надежный способ получения user_id
    if hasattr(message, 'from_user') and message.from_user:
        user_id = message.from_user.id
    elif hasattr(message, 'message') and hasattr(message.message, 'from_user'):
        user_id = message.message.from_user.id
    else:
        bot.reply_to(message, "⛔ Ошибка авторизации.")
        return False
    
    if not is_user_authorized(user_id):
        bot.reply_to(message, "⛔ Доступ запрещен.")
        return False
    return True

    # Декоратор для оборачивания функций, требующих прав (юзера или админа)
def require_auth(bot):
    def decorator(func):
        def wrapper(message, *args, **kwargs):
            # Проверяем, является ли message callback-запросом или обычным сообщением
            user_id = message.from_user.id if hasattr(message, 'from_user') else message.message.from_user.id
            
            if not is_user_authorized(user_id):
                # Отправляем сообщение вместо ответа на callback
                if hasattr(message, 'message'):  # Это callback
                    bot.answer_callback_query(message.id, "⛔ Доступ запрещен")
                else:  # Это обычное сообщение
                    bot.reply_to(message, "⛔ Доступ запрещен. Пожалуйста, авторизуйтесь через /start")
                return
            return func(message, *args, **kwargs)
        return wrapper
    return decorator