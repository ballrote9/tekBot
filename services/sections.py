SECTIONS = {
    "history": {
        "title": "История компании",
        "description": "Редактирование информации об истории компании",
        "allow_file": True,
        "file_types": ["pdf", "image", "video"]
    },
    "values": {
        "title": "Ценности компании",
        "description": "Редактирование информации о ценностях компании",
        "allow_file": True,
        "file_types": ["pdf", "image", "video"]
    },
    "structure": {
        "title": "Организационная структура",
        "description": "🧱 Организационная структура компании — схема управления и подразделений.",
        "allow_file": True,
        "file_types": ["pdf"]
    },
    "canteen": {
        "title": "Столовая",
        "description": "🍽️ Информация о столовой: режим работы, меню на день.",
        "allow_file": True,
        "file_types": ["pdf", "image", "text"]
    },
    "events": {
        "title": "Корпоративные мероприятия",
        "description": "🎉 Корпоративные мероприятия",
        "allow_file": True
    },
    "documents": {
        "title": "Оформление документов",
        "description": "📄 Как оформить документы: отпуск, больничный, справки и т.д.",
        "allow_file": True
    },
    "virtual_tour": {
        "title": "Виртуальный тур по ТЭК",
        "description": "🌐 Виртуальная экскурсия — возможность познакомиться с компанией онлайн.",
        "allow_file": True
    },
    "training_materials_pdf": {
        "title": "PDF-файлы",
        "description": "📄 Обучающие PDF-документы",
        "allow_file": True,
        "file_types": ["pdf"]
    },
    "training_materials_video": {
        "title": "Видеоматериалы",
        "description": "🎥 Видео для обучения",
        "allow_file": True,
        "file_types": ["mp4", "mov", "avi"]
    },
    "training_materials_presentation": {
        "title": "Презентации",
        "description": "📊 Обучающие презентации",
        "allow_file": True,
        "file_types": ["pptx", "ppt"]
    },
    "training_materials": {
        "title": "Обучающие материалы",
        "description": "🎓 Материалы для обучения новых сотрудников",
        "allow_file": True,
        "allow_test": True,  # Добавляем флаг для тестов
        "file_types": ["pdf", "presentation", "video"]
    },
    "company_tours": {
        "title": "Экскурсии по компании",
        "description": "Добавление и редактирование информации об экскурсиях"
    },
    "greetings": {
        "title": "Приветственное сообщение",
        "description": "Привет! 👋 Я ваш персональный помощник по онбордингу — всегда готов помочь вам быстро адаптироваться и найти нужную информацию." + "\n\nВот что я могу:" + 
            "\n🔹 Рассказать об истории, миссии и ценностях компании\n🔹 Поделиться полезными материалами для новых сотрудников\n🔹 Ответить на частые вопросы (FAQ)" +
            "\n🔹 Принять обратную связь и помочь с поддержкой\n\n📌 Как со мной взаимодействовать:\nВы всегда можете использовать команду /menu" + 
            "\nПросто выберите интересующий вас раздел из меню ниже: ",
        "allow_file": False
    },
    "contact_admin": {
        "title": "Список администраторов:",
        "description": "@sia_it",
        "allow_file": False
    },
    "search_emp": {
        "title": "Поиск конткактной информации о сотрудниках:",
        "description": "Введите ФИО сотрудника:",
        "allow_file": False
    }
}