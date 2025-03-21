from fastapi import HTTPException

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import os
from dotenv import load_dotenv

load_dotenv()  # Загружает переменные окружения из файла .env

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(SQLALCHEMY_DATABASE_URL)

# создаем таблицы
# Base.metadata.create_all(bind=engine)

SessionLocal = sessionmaker(autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
        db.commit()  # Коммитим изменения, если все прошло успешно
    except Exception as e:
        db.rollback()  # Откатываем транзакцию в случае ошибки
        raise HTTPException(status_code=500, detail="Database error occurred")  # Генерируем HTTP-ошибку
    finally:
        db.close()  # Закрываем сессию