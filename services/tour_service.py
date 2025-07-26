# services/tour_service.py

from database.models import TourRegistration, CompanyTour, User_info
from datetime import datetime
tour_message_ids = {}
def register_user_for_tour(db, tour_id, user_id):
    user_info = db.query(User_info).filter_by(auth_token=str(user_id)).first()
    if not user_info:
        return False, "Пользователь не найден"

    existing = db.query(TourRegistration).filter_by(
        tour_id=tour_id,
        user_auth_token=user_info.auth_token
    ).first()
    if existing:
        return False, "Вы уже зарегистрированы"

    tour = db.query(CompanyTour).filter_by(id=tour_id).first()
    if not tour:
        return False, "Экскурсия не найдена"

    if len(tour.registrations) >= tour.max_participants:
        return False, "Мест больше нет"

    registration = TourRegistration(
        tour_id=tour_id,
        user_auth_token=user_info.auth_token,
        registered_at=datetime.now()
    )
    db.add(registration)
    db.commit()
    db.refresh(tour)

    return True, tour
