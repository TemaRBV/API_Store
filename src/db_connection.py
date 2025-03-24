from fastapi import HTTPException

from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

import os
from dotenv import load_dotenv

load_dotenv()  # Загружает переменные окружения из файла .env

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_async_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(class_=AsyncSession, autoflush=False, bind=engine)


async def get_db() -> AsyncSession:
    async with SessionLocal() as db:
        try:
            yield db
            await db.commit()  # Коммитим изменения, если все прошло успешно
        except Exception as e:
            await db.rollback()  # Откатываем транзакцию в случае ошибки
            raise HTTPException(status_code=500, detail=e)  # Генерируем HTTP-ошибку
        finally:
            await db.close()  # Закрываем сессию