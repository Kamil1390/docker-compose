import pika
import psycopg2
import time
from typing import List
import os


rabbitmq_parametrs = {
    'host': os.environ['RABBITMQ_HOST'],
    'port': int(os.environ['RABBITMQ_PORT']),
}

db_parametrs = {
    'host': os.environ['POSTGRES_HOST'],
    'database': os.environ['POSTGRES_DB'],
    'user': os.environ['POSTGRES_USER'],
    'password': os.environ['POSTGRES_PASSWORD'],
}


def write_to_database(mesage: List[str]) -> None:
    try:
        with psycopg2.connect(**db_parametrs) as db_connection:
            print("Connect is succes!")
            with db_connection.cursor() as cursor:
                table_name = mesage.pop(0)
                cursor.execute("""
                    SELECT column_name
                    FROM information_schema.columns
                    WHERE table_name = %s
                    ORDER BY ordinal_position;
                """, (table_name,))
                columns = [row[0] for row in cursor.fetchall()]
                columns.pop(0) if columns[0] != 'symbol' else None
                while columns[0] != 'symbol':
                    columns.pop(0)
                columns = columns[:len(mesage)]
                cursor.execute(
                    f"""
                    Insert Into {table_name}({','.join(columns)})
                    Values ({','.join('%s' for _ in range(len(mesage)))})
                    """,
                    tuple(mesage)
                )
    except psycopg2.Error as ex:
        print(f"Error: {ex}")


def callback(ch, method, properties, body: str) -> None:
    message = body.decode('utf-8').split(',')
    write_to_database(message)


time.sleep(30)
connection = pika.BlockingConnection(
    pika.ConnectionParameters(**rabbitmq_parametrs))
print('Begin')
chanel = connection.channel()
chanel.queue_declare(queue='python-queue')
chanel.basic_consume(queue='python-queue',
                     on_message_callback=callback, auto_ack=True)
chanel.start_consuming()
