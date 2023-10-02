#!/bin/bash
# Регистрация пользователей.
curl -H 'Content-Type: application/json' --data '{
    "email":"livesey@test.com",
    "username": "test1",
    "first_name": "Doctor",
    "last_name": "Livesey",
    "password": "wd5jzxrT."
}' http://127.0.0.1:8000/api/users/
curl -H 'Content-Type: application/json' --data '{
    "email":"user2@test.com",
    "username": "user2",
    "first_name": "Doctor",
    "last_name": "Livesey",
    "password": "wd5jzxrT."
}' http://127.0.0.1:8000/api/users/
curl -H 'Content-Type: application/json' --data '{
    "email":"user3@test.com",
    "username": "user3",
    "first_name": "Doctor",
    "last_name": "Livesey",
    "password": "wd5jzxrT."
}' http://127.0.0.1:8000/api/users/

# Логиним пользователя получаем токен
# curl -H 'Content-Type: application/json' --data '{
#     "email":"livesey@test.com",
#     "password": "wd5jzxrT."
# }' http://127.0.0.1:8000/api/auth/token/login/