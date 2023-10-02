import json

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

    with open('./data/ingredients.json') as json_file:
        data = json.load(json_file)

    columns = ['name', 'measurement_unit']
    for row in data:
        keys = tuple(row[c] for c in columns)
        cursor.execute(
            "INSERT INTO recipes_ingredient (name, measurement_unit)"
            "VALUES (%s, %s)", keys
        )

    connection.commit()
    print("Ингредиенты успешно добавлены")

except (Exception, Error) as error:
    print("Ошибка при работе с PostgreSQL", error)
finally:
    if connection:
        cursor.close()
        connection.close()
        print("Соединение с PostgreSQL закрыто")
