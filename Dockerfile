# Используем официальный образ Python
FROM python:3.12-slim

# Установка необходимых системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Установка Poetry
RUN pip install poetry

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы конфигурации Poetry
COPY src/pyproject.toml src/poetry.lock* ./

# Установка зависимостей
RUN poetry install --no-root

# Копируем все файлы приложения в контейнер
COPY src/ ./

# Проверка установленных пакетов (для отладки)
RUN poetry show

# Открытие порта
EXPOSE 8000

# Указываем команду для запуска приложения
CMD ["poetry", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]