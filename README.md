# tekBot
Tg-bot Tg-api

Точка входа: core.py 

handlers/start_handler.py
В этом файле реализована логика входа по заранее выданному паролю.
Такие основные команды, как: /start, /menu, /profile, /greetings.

Основное меню:
Кнопки описаны в handlers/start_handler.py
Обработка их колбеков описана в handlers/menu_handler.py, handlers/info_handler.py,
handlers/emp_info_handler.py

Меню "Информация о компании":
Описано в handlers/info_handler.py

Меню "Информация для сотрудников":
Описано в handlers/emp_info_handler.py

БД:
Таблицы представлены в файле database/models.py, 
подключение БД происходит в database/session.py, database/content_session.py
Так же для начального этапа работы можно пользоваться файлами innit_<название>, 
они инициализируют БД начальными значениями.

handlers/admin_content_callback_handler
Очень важная часть, здесь описывается способ работы с содержимым типовых секций (Столовая, Ценности компании и т.д.)
Краткое  описание работы: ловятся колбеки начинающиеся с edit_section:, и имеющие вид: edit_section:<название_секции>:<колбек_для_кнопки_"назад">
Благодаря чему, этот общий шаблон подходит для работы с разными секциями.

Безопасность:
Все функции обернуты в декоратор из services/auth_check.py, который требует, чтобы пользователь был авторизован по паролю,
выдаваемый админом (пароли хранятся в data/user_passwords.csv, генерируются в innit_users.py) либо пользователь должен быть
в таблице Admins, где хранятся telegrammID админов.