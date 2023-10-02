import json
import sqlite3


def main():
    connection = sqlite3.connect('../db.sqlite3')
    cursor = connection.cursor()
    with open('../data/ingredients.json') as json_file:
        data = json.load(json_file)

    columns = ['name', 'measurement_unit']
    for row in data:
        keys = tuple(row[c] for c in columns)
        cursor.execute(
            "INSERT INTO recipes_ingredient (name, measurement_unit)"
            "VALUES (?, ?)", keys
        )
    connection.commit()
    connection.close()
    print('[+++]Ingredients added!')


if __name__ == '__main__':
    main()
