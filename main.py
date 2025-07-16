import pandas as pd
import secrets
import hashlib
from database.models import User, User_info
from database.session import SessionLocal, engine, Base
import os


# Создаем таблицы, если их нет
Base.metadata.create_all(bind=engine)

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def generate_unique_code() -> str:
    return secrets.token_urlsafe(8)

def import_employees_from_csv(csv_path: str):
    db = SessionLocal()

    df = pd.read_csv(csv_file, encoding='utf-16', sep='\s{2,}', engine='python')
    user_pwd = []
    for _, row in df.iterrows():
        name = row['name']
        mail = row['mail']
        office = row['office']
        officephone = row['officephone']

        auth_token = generate_unique_code()
        pwd = generate_unique_code()
        hashpass = hash_password(pwd)

        user_pwd.append({
            'auth_token':auth_token,
            'name':name,
            'pwd':pwd
        })

        # Добавляем запись User_info
        user_info = User_info(
            full_name=name,
            mail=mail,
            office=office,
            officephone=officephone,
            auth_token=auth_token
        )

        # Добавляем запись User
        user = User(
            auth_token=auth_token,
            hash_pass=hashpass,
            is_authorized=False
        )

        db.add(user_info)
        db.add(user)

        print(f"[{name}] Token: {auth_token}")

    db.commit()
    db.close()
    new_df = pd.DataFrame(user_pwd)
    new_df.to_csv('data/user_passwords.csv', index=False, sep='\t', encoding='utf-8')


if __name__ == "__main__":
    csv_file = "data/users.csv"
    import_employees_from_csv(csv_file)