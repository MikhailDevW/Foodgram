import psycopg2
from psycopg2 import Error

try:
    connection = psycopg2.connect(
        user="admin",
        password="mysecretpassword",
        host="db",
        port="5432",
        database="foodgram_db"
    )
    cursor = connection.cursor()
    tags = [
        ('Завтрак', '#DAA520', 'breakfast',),
        ('Обед', '#3CB371', 'dinner',),
        ('Ужин', '#FA8072', 'lunch',),
        ('Ночной дожор', '#000000', 'junkfood'),
    ]
    # cursor.execute(insert_query)
    cursor.executemany(
        "INSERT INTO recipes_tag (name, color, slug)"
        "VALUES (%s, %s, %s)", tags
    )
    connection.commit()
    print("Запись успешно вставлена")

except (Exception, Error) as error:
    print("Ошибка при работе с PostgreSQL", error)
finally:
    if connection:
        cursor.close()
        connection.close()
        print("Соединение с PostgreSQL закрыто")
