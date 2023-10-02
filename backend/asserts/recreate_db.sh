#!/bin/bash
echo "Starting recreate DB..."
rm ../db.sqlite3
rm ../user/migrations/*_initial.py
rm ../recipes/migrations/*_initial.py
echo "[+]Migrations and DB deleted."
source ../venv/bin/activate
python ../manage.py makemigrations
python ../manage.py migrate
echo "[++]Migrations complete."

# email="admin@mail.com"
# username="admin"
# name="Livesey"
# sname="Doc"
# password="DocLivesey!!!"
# python backend/manage.py createsuperuser

python adding_db_tags.py
python adding_db_ingredients.py
python ../manage.py runserver
