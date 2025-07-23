# handlers/admin_tour_handler.py

from telebot import types
from database.models import CompanyTour, User_info, TourRegistration
from database.session import SessionLocal
from datetime import datetime

from handlers.emp_info_handler import show_company_tours
from services.auth_check import require_auth

def register_admin_tour_handlers(bot):
    @bot.callback_query_handler(func=lambda call: call.data == "add_tour")
    @require_auth(bot)
    def request_tour_title(call):
        msg = bot.send_message(call.message.chat.id, "Введите название экскурсии:")
        bot.register_next_step_handler(msg, request_tour_description)

    def request_tour_description(message):
        title = message.text.strip()
        msg = bot.send_message(message.chat.id, "Введите описание экскурсии:")
        bot.register_next_step_handler(msg, request_tour_time, title)

    def request_tour_time(message, title):
        description = message.text.strip()
        msg = bot.send_message(message.chat.id, "Введите дату и время (в формате 01.08.2025 10:00):")
        bot.register_next_step_handler(msg, request_tour_place, title, description)

    def request_tour_place(message, title, description):
        try:
            time = datetime.strptime(message.text.strip(), "%d.%m.%Y %H:%M")
        except ValueError:
            bot.send_message(message.chat.id, "❌ Неверный формат даты. Попробуйте снова.")
            return

        msg = bot.send_message(message.chat.id, "Введите место сбора:")
        bot.register_next_step_handler(msg, save_tour, title, description, time)

    def save_tour(message, title, description, time):
        place = message.text.strip()
        db = SessionLocal()
        new_tour = CompanyTour(
            title=title,
            description=description,
            meeting_time=time,
            meeting_place=place
        )
        db.add(new_tour)
        db.commit()
        db.refresh(new_tour)
        bot.send_message(message.chat.id, "✅ Экскурсия успешно добавлена")

        # Рассылка всем сотрудникам
        users = db.query(User_info).all()
        for user in users:
            try:
                bot.send_message(
                    user.auth_token,
                    f"📢 Новая экскурсия: {title}\n"
                    f"📅 {time.strftime('%d.%m.%Y %H:%M')}\n"
                    f"📍 {place}\n\n"
                    f"Нажмите, чтобы записаться"
                )
            except:
                continue

    @bot.callback_query_handler(func=lambda call: call.data == "delete_tour")
    def show_tours_for_deletion(call):
        db = SessionLocal()
        try:
            tours = db.query(CompanyTour).filter(CompanyTour.is_active == True).all()

            if not tours:
                bot.answer_callback_query(call.id, "Нет активных экскурсий для удаления.")
                return

            markup = types.InlineKeyboardMarkup(row_width=1)
            for tour in tours:
                btn = types.InlineKeyboardButton(
                    f"🗑 {tour.title} ({tour.meeting_time.strftime('%d.%m %H:%M')})",
                    callback_data=f"confirm_delete_tour:{tour.id}"
                )
                markup.add(btn)

            markup.add(types.InlineKeyboardButton("⬅ Назад", callback_data="company_tours"))

            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text="Выберите экскурсию для удаления:",
                reply_markup=markup
            )
        except Exception as e:
            print(f"Ошибка при отображении экскурсий для удаления: {e}")
            bot.send_message(call.message.chat.id, "Произошла ошибка.")
        finally:
            db.close()

    @bot.callback_query_handler(func=lambda call: call.data.startswith("confirm_delete_tour:"))
    def confirm_delete_tour(call):
        try:
            tour_id = int(call.data.split(":")[1])
        except (ValueError, IndexError):
            bot.answer_callback_query(call.id, "Неверный ID экскурсии.")
            return

        db = SessionLocal()
        try:
            tour = db.query(CompanyTour).filter_by(id=tour_id, is_active=True).first()
            if not tour:
                bot.answer_callback_query(call.id, "Экскурсия не найдена или уже удалена.")
                return

            # Кнопки подтверждения
            markup = types.InlineKeyboardMarkup(row_width=2)
            markup.add(
                types.InlineKeyboardButton("✅ Да, удалить", callback_data=f"do_delete_tour:{tour_id}"),
                types.InlineKeyboardButton("❌ Отмена", callback_data="delete_tour")
            )

            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=f"Вы уверены, что хотите удалить экскурсию?\n\n"
                     f"🏛 <b>{tour.title}</b>\n"
                     f"📅 {tour.meeting_time.strftime('%d.%m.%Y %H:%M')}\n"
                     f"📍 {tour.meeting_place}\n\n"
                     f"Экскурсия будет удалена, и записаться будет нельзя.",
                parse_mode='HTML',
                reply_markup=markup
            )
        except Exception as e:
            print(f"Ошибка при подтверждении удаления: {e}")
            bot.send_message(call.message.chat.id, "Произошла ошибка.")
        finally:
            db.close()

    @bot.callback_query_handler(func=lambda call: call.data.startswith("do_delete_tour:"))
    def do_delete_tour(call):
        try:
            tour_id = int(call.data.split(":")[1])
        except (ValueError, IndexError):
            bot.answer_callback_query(call.id, "❌ Неверный ID экскурсии.")
            return

        db = SessionLocal()
        try:
            # Находим экскурсию
            tour = db.query(CompanyTour).filter_by(id=tour_id).first()
            if not tour:
                bot.answer_callback_query(call.id, "❌ Экскурсия не найдена.")
                return

            # Удаляем все регистрации на эту экскурсию
            db.query(TourRegistration).filter_by(tour_id=tour_id).delete()

            # Удаляем саму экскурсию
            db.delete(tour)
            db.commit()

            bot.answer_callback_query(call.id, "✅ Экскурсия и все записи на неё успешно удалены!")

            # Возвращаем обновлённый список экскурсий
            show_company_tours(bot, call.message)

        except Exception as e:
            db.rollback()
            print(f"Ошибка при удалении экскурсии: {e}")
            bot.answer_callback_query(call.id, "⚠️ Ошибка при удалении экскурсии.")
        finally:
            db.close()
