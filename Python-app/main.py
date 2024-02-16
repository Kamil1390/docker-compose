import pika
import psycopg2
import socket
import time
from typing import List


rabbitmq_parametrs = {
    'host': 'rabbit',
    'port': '5672',
}

db_parametrs = {
    'host': 'postgres',
    'database': 'POSTGRES_DB',
    'user': 'POSTGRES_USER',
    'password': 'POSTGRES_PASSWORD',
}


def wait_for_service(host, port, max_attempts=30, timeout=1):
    attempts = 0
    while attempts < max_attempts:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex((host, port))
        sock.close()
        if result == 0:
            print(f"Service {host}:{port} is available.")
            return True
        else:
            attempts += 1
            print(
                f"Attempt {attempts}/{max_attempts} failed. Retrying in {timeout} second(s).")
            time.sleep(timeout)
    raise Exception(
        f"Failed to connect to {host}:{port} after multiple attempts.")


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


wait_for_service('rabbit', 5672)

connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbit'))
chanel = connection.channel()
chanel.queue_declare(queue='python-queue')
chanel.basic_consume(queue='python-queue',
                     on_message_callback=callback, auto_ack=True)
chanel.start_consuming()
