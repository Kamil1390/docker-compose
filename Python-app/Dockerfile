FROM python:3.11

# Создание рабочей директории
WORKDIR /app

# Установка библиотек для работы с postgresql и rabbitmq
RUN pip install psycopg2-binary
RUN pip install pika

COPY . .


CMD [ "python3.11", "main.py" ]