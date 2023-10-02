import sqlite3


def main():
    con = sqlite3.connect('../db.sqlite3')
    cur = con.cursor()

    # данные для тегов
    tags = [
        ('Завтрак', '#DAA520', 'breakfast',),
        ('Обед', '#3CB371', 'dinner',),
        ('Ужин', '#FA8072', 'lunch',),
        ('Ночной дожор', '#000000', 'junkfood'),
    ]
    cur.executemany(
        "INSERT INTO recipes_tag (name, color, slug)"
        "VALUES (?, ?, ?)", tags
    )
    con.commit()
    print('[+++]Tags added!!')


if __name__ == '__main__':
    main()
