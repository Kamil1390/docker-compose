FROM postgres:latest

# Загрузка значений переменных окружения из файла .env
ENV POSTGRES_DB="f_base"
ENV POSTGRES_USER="Kamil"
ENV POSTGRES_PASSWORD="12345"

# Копирование SQL-скрипта для заполнения таблиц
COPY init.sql /docker-entrypoint-initdb.d/
COPY fut_tabl.csv /docker-entrypoint-initdb.d/
COPY daily_tabl.csv /docker-entrypoint-initdb.d/
COPY details_tabl.csv /docker-entrypoint-initdb.d/