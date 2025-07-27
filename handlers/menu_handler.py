from telebot import types

from database.session import SessionLocal
from services.auth_check import require_auth
from database.models import Content, ContentFile, UserTestProgress, CompanyTour, User_info, TourRegistration, Admin
from database.content_session import ContentSessionLocal  # Импорт сессии БД
import os
from datetime import datetime
from handlers.feedback_handler import request_feedback_text, show_feedbacks, ask_feedback
from handlers.reminders_handler import (
    save_reminder,
    request_reminder_schedule,
    show_reminders_menu,
    request_reminder_text,
    show_scheduled_reminders,
    request_reminder_to_delete
)
from handlers.analytics_handler import (
    show_analytics_menu, 
    generate_users_report, 
    generate_feedback_report,
    generate_reminders_report,
    generate_tests_report,
    generate_content_report,
    create_excel_file  # Импортируем функцию создания Excel
)
from services.content_service import show_content
from services.tour_service import tour_message_ids


def register_menu_handlers(bot):
    def handle_training_search_input(message):
        query = message.text.strip().lower()
        if len(query) < 2:
            bot.send_message(message.chat.id, "🔍 Введите минимум 2 символа для поиска")
            return

        db = ContentSessionLocal()
        try:
            training_sections = [
                "training_materials_pdf",
                "training_materials_video", 
                "training_materials_presentation"
            ]

            # Ищем контент в обучающих разделах
            results = db.query(Content).filter(
                Content.section.in_(training_sections)
            ).all()

            found_files = False
            for content in results:
                for file in content.files:
                    # Получаем только имя файла (без пути)
                    file_name = os.path.basename(file.file_path).lower()
                    
                    # Проверяем совпадение с запросом
                    if query in file_name:
                        if os.path.exists(file.file_path):
                            try:
                                with open(file.file_path, 'rb') as f:
                                    bot.send_document(
                                        message.chat.id,
                                        f,
                                        visible_file_name=os.path.basename(file.file_path)
                                    )
                                    found_files = True
                            except Exception as e:
                                print(f"Ошибка отправки файла: {e}")
                        else:
                            print(f"Файл не существует: {file.file_path}")

            if not found_files:
                bot.send_message(message.chat.id, "❌ В обучающих материалах ничего не найдено")

        except Exception as e:
            print(f"Ошибка при поиске: {e}")
            bot.send_message(message.chat.id, "⚠ Ошибка при выполнении поиска")
        finally:
            db.close()
            
    @bot.callback_query_handler(func=lambda call: call.data == "analytics_menu")
    @require_auth(bot)
    def handle_analytics_menu(call):
        show_analytics_menu(bot, call.message)

    @bot.callback_query_handler(func=lambda call: call.data.startswith("report:"))
    @require_auth(bot)
    def handle_report_request(call):
        report_type = call.data.split(":")[1]
        
        if report_type == "users":
            report, excel_data = generate_users_report()
            bot.send_message(call.message.chat.id, report)
            
            # Отправка Excel файла
            excel_file, filename = create_excel_file(excel_data, "users_report.xlsx")
            bot.send_document(call.message.chat.id, excel_file, visible_file_name=filename)
            
        elif report_type == "feedback":
            report, excel_data = generate_feedback_report()
            bot.send_message(call.message.chat.id, report)
            
            # Отправка Excel файла
            excel_file, filename = create_excel_file(excel_data, "feedback_report.xlsx")
            bot.send_document(call.message.chat.id, excel_file, visible_file_name=filename)
        
        elif report_type == "reminders":
            # генерируем и отправляем отчёт по напоминаниям
            report, data = generate_reminders_report()
            bot.send_message(call.message.chat.id, report)

            # создаём Excel и шлём файл
            excel_file, filename = create_excel_file(data, "reminders_report.xlsx")
            bot.send_document(call.message.chat.id, excel_file, visible_file_name=filename)
            
        elif report_type == "tests":
            report, excel_data = generate_tests_report()
            bot.send_message(call.message.chat.id, report)
            excel_file, filename = create_excel_file(excel_data, "tests_report.xlsx")
            bot.send_document(call.message.chat.id, excel_file, visible_file_name=filename)

        elif report_type == "content":
            report, excel_data = generate_content_report()
            bot.send_message(call.message.chat.id, report)
            excel_file, filename = create_excel_file(excel_data, "content_report.xlsx")
            bot.send_document(call.message.chat.id, excel_file, visible_file_name=filename)
            
    @bot.callback_query_handler(func=lambda call: call.data == "send_reminder")
    @require_auth(bot)
    def handle_send_reminder(call):
        request_reminder_text(bot, call)

    @bot.callback_query_handler(func=lambda call: call.data == "configure_reminders")
    @require_auth(bot)
    def handle_configure_reminders(call):
        show_scheduled_reminders(bot, call)

    @bot.callback_query_handler(func=lambda call: call.data == "delete_reminder_menu")
    @require_auth(bot)
    def handle_delete_reminder_menu(call):
        request_reminder_to_delete(bot, call)

    @bot.callback_query_handler(func=lambda call: call.data.startswith("reminder_type:"))
    @require_auth(bot)
    def handle_reminder_type(call):
        parts = call.data.split(":", 2)
        r_type = parts[1]
        text = parts[2]
        
        if r_type == "instant":
            # Сохраняем и отправляем немедленно
            if save_reminder(bot, text, is_instant=True):
                bot.send_message(call.message.chat.id, "✅ Напоминание отправлено всем пользователям!")
            else:
                bot.send_message(call.message.chat.id, "⚠️ Ошибка при отправке напоминания")
        else:
            # Запрашиваем интервал для повторяющихся напоминаний
            request_reminder_schedule(bot, call, text)

    @bot.callback_query_handler(func=lambda call: call.data.startswith("reminder_interval:"))
    @require_auth(bot)
    def handle_reminder_interval(call):
        parts = call.data.split(":", 2)
        interval = parts[1]
        text = parts[2]
        
        # Сохраняем напоминание с интервалом
        if save_reminder(bot, text, interval=interval):
            bot.send_message(call.message.chat.id, f"✅ Повторяющееся напоминание настроено ({interval})!")
        else:
            bot.send_message(call.message.chat.id, "⚠️ Ошибка при настройке напоминания")
            
    @bot.callback_query_handler(func=lambda call: call.data == "give_feedback")
    @require_auth(bot)
    def handle_give_feedback(call):
        request_feedback_text(bot, call)

    @bot.callback_query_handler(func=lambda call: call.data == "view_feedbacks")
    @require_auth(bot)
    def handle_view_feedbacks(call):
        show_feedbacks(bot, call)

    @bot.callback_query_handler(func=lambda call: call.data == "take_quiz")
    @require_auth(bot)
    def handle_take_quiz(call):
        bot.send_message(call.message.chat.id, "📝 Опрос находится в разработке")
        ask_feedback(bot, call.message)  # Вернуться в меню обратной связи
        
        
    @bot.callback_query_handler(func=lambda call: call.data.startswith("edit_tests_section:"))
    @require_auth(bot)
    def handle_edit_tests(call):
        from handlers.tests_handler import show_edit_tests_menu
        show_edit_tests_menu(bot, call.message, call.from_user.id)
        bot.answer_callback_query(call.id)  # Важно: подтверждаем обработку callback
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith("edit_test:"))
    @require_auth(bot)
    def handle_edit_test(call):
        test_id = int(call.data.split(":")[1])
        # Реализуйте логику редактирования теста
        bot.send_message(call.message.chat.id, f"Редактирование теста ID: {test_id}")

    @bot.callback_query_handler(func=lambda call: call.data == "add_new_test")
    @require_auth(bot)
    def handle_add_new_test(call):
        # Реализуйте логику добавления нового теста
        bot.send_message(call.message.chat.id, "Добавление нового теста")
        
    @bot.callback_query_handler(func=lambda call: call.data.startswith("test_start:"))
    @require_auth(bot)
    def handle_test_start(call):
        from database.session import SessionLocal
        test_id = int(call.data.split(":")[1])
        db = SessionLocal()
        
        # Отмечаем тест как пройденный
        progress = db.query(UserTestProgress).filter(
            UserTestProgress.user_id == call.from_user.id,
            UserTestProgress.test_id == test_id
        ).first()
        
        if not progress:
            progress = UserTestProgress(
                user_id=call.from_user.id,
                test_id=test_id,
                completed=True,
                completed_at=datetime.now()
            )
            db.add(progress)
        elif not progress.completed:
            progress.completed = True
            progress.completed_at = datetime.now()
        
        db.commit()
        db.close()
        
        bot.answer_callback_query(call.id, "Тест отмечен как пройденный!")

    @bot.callback_query_handler(func=lambda call: call.data.startswith("register_tour:"))
    @require_auth(bot)
    def handle_register_tour(call):
        tour_id = int(call.data.split(":")[1])
        user_token = str(call.from_user.id)

        db = SessionLocal()
        try:
            tour = db.query(CompanyTour).get(tour_id)

            if not tour:
                bot.answer_callback_query(call.id, "Экскурсия не найдена")
                return

            if len(tour.registrations) >= tour.max_participants:
                bot.answer_callback_query(call.id, "Мест больше нет")
                return

            existing = db.query(TourRegistration).filter(
                TourRegistration.tour_id == tour_id,
                TourRegistration.user_auth_token == user_token
            ).first()

            if existing:
                bot.answer_callback_query(call.id, "Вы уже записаны")
                return

            registration = TourRegistration(
                tour_id=tour_id,
                user_auth_token=user_token
            )
            db.add(registration)
            db.commit()
            db.refresh(tour)

            bot.answer_callback_query(call.id, "Вы записались!")
            bot.send_message(
                call.message.chat.id,
                f"✅ Вы записаны на '{tour.title}' в {tour.meeting_time.strftime('%d.%m.%Y %H:%M')}"
            )

            # ✅ Обновление счётчика
            count = db.query(TourRegistration).filter(
                TourRegistration.tour_id == tour_id
            ).count()

            chat_id = call.message.chat.id
            message_id = tour_message_ids.get((chat_id, tour_id))
            if message_id:
                updated_text = (
                    f"🏛 {tour.title}\n"
                    f"🕒 {tour.meeting_time.strftime('%d.%m.%Y %H:%M')}\n"
                    f"📍 {tour.meeting_place}\n"
                    f"📝 {tour.description or 'Описание отсутствует'}\n\n"
                    f"Участников: {count} / {tour.max_participants}"
                )

                reg_button = types.InlineKeyboardButton(
                    "✅ Записаться",
                    callback_data=f"register_tour:{tour.id}"
                )
                tour_markup = types.InlineKeyboardMarkup()
                tour_markup.add(reg_button)

                try:
                    bot.edit_message_text(
                        chat_id=chat_id,
                        message_id=message_id,
                        text=updated_text,
                        reply_markup=tour_markup
                    )
                except Exception as e:
                    print(f"[ERROR] Не удалось обновить сообщение: {e}")


            admins = db.query(Admin).all()
            for admin in admins:
                try:
                    bot.send_message(
                        admin.auth_token,
                        f"🔔 Новая запись на экскурсию:\n"
                        f"🏛 {tour.title}\n"
                        f"🕒 {tour.meeting_time.strftime('%d.%m.%Y %H:%M')}"
                    )
                except Exception as e:
                    print(f"[WARN] Не удалось отправить уведомление админу {admin.auth_token}: {e}")

        except Exception as e:
            print(f"[REG ERROR] {e}")
            bot.answer_callback_query(call.id, "❌ Ошибка при записи")
        finally:
            db.close()

    @bot.callback_query_handler(func=lambda call: True)
    @require_auth(bot)
    def handle_callback(call):     
        # —————— Обновление last_activity ——————
        from datetime import datetime
        from database.models import User
        from database.session import SessionLocal

        db = SessionLocal()
        user = db.query(User).filter(User.auth_token == str(call.from_user.id)).first()
        if user:
            user.last_activity = datetime.now()
            db.commit()
        db.close()
        # ————————————————————————————————
        # --- Подменю "Информация для сотрудников" ---
        # --- Главное меню ---
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.auth_token == str(call.from_user.id)).first()
            if user:
                user.last_activity = datetime.now()
                db.commit()
        except:
            pass
        finally:
            db.close()
        

        # информация для сотрудников
        # FAQ
        if call.data == "faq":
            from handlers.faq_handler import show_faq_menu
            show_faq_menu(bot, call.message)
        # Обратная связь
        elif call.data == "feedback":
            from handlers.feedback_handler import ask_feedback
            ask_feedback(bot, call.message)
        # Поддержка
        elif call.data == "support":
            from handlers.support_handler import show_support
            show_support(bot, call.message)
        # Конец меню
        
        elif call.data == "contact_admin":
            markup = types.InlineKeyboardMarkup(row_width=1)
            uid = call.from_user.id
            is_admin = (
                db.query(Admin).filter(Admin.auth_token == uid).first() is not None
            )
            markup = types.InlineKeyboardMarkup(row_width=1)
            if is_admin:
                buttons = [ 
                    types.InlineKeyboardButton("Связаться с администраторами ", callback_data="contact_admin"),
                    types.InlineKeyboardButton("⬅ Назад", callback_data="back_to_main")
                ]
            else:
                buttons = [
                    types.InlineKeyboardButton("⬅ Назад", callback_data="back_to_main")
                ]

            markup.add(*buttons)
            show_content(bot, call, markup)

        elif call.data == "training_tests":
            from handlers.tests_handler import show_tests_menu
            show_tests_menu(bot, call.message, call.from_user.id)
            
        elif call.data == "training_categories":
            from handlers.training_materials import show_training_categories
            show_training_categories(bot, call)
    
        elif call.data == "training_search":
            bot.send_message(call.message.chat.id, "Введите начало названия материала для поиска:")
            bot.register_next_step_handler(call.message, handle_training_search_input)
            
        elif call.data.startswith("training_section:"):
            section = call.data.split(":", 1)[1]
            if section == "training_tests":
                from handlers.tests_handler import show_tests_menu
                show_tests_menu(bot, call.message, call.from_user.id)
            else:
                from handlers.training_materials import show_training_by_section
                show_training_by_section(bot, call, section)
            
        elif call.data == "faq_list":
            from handlers.faq_handler import show_question_list
            show_question_list(bot, call)

        elif call.data.startswith("faq_show:"):
            from handlers.faq_handler import show_question_detail
            question_id = int(call.data.split(":")[1])
            show_question_detail(bot, call, question_id)

        elif call.data == "faq_ask":
            from handlers.faq_handler import ask_question
            ask_question(bot, call.message)

        elif call.data == "faq_admin":
            from handlers.faq_handler import show_unanswered_questions
            show_unanswered_questions(bot, call)

        elif call.data.startswith("faq_admin_detail:"):
            from handlers.faq_handler import show_question_admin_options
            question_id = int(call.data.split(":")[1])
            show_question_admin_options(bot, call, question_id)

        elif call.data.startswith("faq_answer:"):
            from handlers.faq_handler import request_answer
            question_id = int(call.data.split(":")[1])
            request_answer(bot, call, question_id)

        elif call.data.startswith("faq_delete:"):
            from handlers.faq_handler import confirm_delete_question
            question_id = int(call.data.split(":")[1])
            confirm_delete_question(bot, call, question_id)

        elif call.data.startswith("faq_delete_confirm:"):
            from handlers.faq_handler import delete_question_handler
            question_id = int(call.data.split(":")[1])
            delete_question_handler(bot, call, question_id)

        elif call.data == "back_to_main":
            from handlers.start_handler import show_main_menu
            show_main_menu(bot, call.message)
        
        elif call.data == "greetings":
            from handlers.start_handler import greetings
            greetings(bot, call.message)
        
        else:
            bot.answer_callback_query(call.id, "Функция пока не реализована")
