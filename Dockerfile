FROM python:3.9-slim

# Установка необходимых библиотек
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование вашего кода в контейнер
WORKDIR /app
COPY src/bot.py /app/
COPY src/simulation.py /app/


# Запуск вашего скрипта
CMD ["python", "bot.py"]