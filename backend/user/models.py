from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models

EMAIL_MAX_LENGTH = 254
FIRST_NAME_MAX_LENGTH = 150
LAST_NAME_MAX_LENGTH = 150
PASSWORD_MAX_LENGTH = 150


class CustomUser(AbstractUser):
    email = models.EmailField(
        'Электронная почта',
        max_length=254,
        blank=False,
        unique=True,
    )
    first_name = models.CharField(
        'Имя',
        max_length=settings.USER_MODEL_SETTINGS.get(
            'first_name_max_length',
            FIRST_NAME_MAX_LENGTH,
        ),
        blank=False,
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=settings.USER_MODEL_SETTINGS.get(
            'last_name_max_length',
            LAST_NAME_MAX_LENGTH,
        ),
        blank=False,
    )
    password = models.CharField(
        'Пароль',
        max_length=settings.USER_MODEL_SETTINGS.get(
            'password_max_length',
            PASSWORD_MAX_LENGTH,
        ),
        blank=False,
    )
    subscribes = models.ManyToManyField(
        'self',
        symmetrical=False,
        related_name='user',
    )

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self) -> str:
        return self.email
