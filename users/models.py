from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Кастомная модель пользователя, заменяющая стандартную модель.

    Вместо поля `username` используется `email` как уникальный идентификатор
    для аутентификации. Позволяет хранить дополнительную информацию о пользователе:
    телефон, город, аватар.

    email (EmailField): Уникальный адрес электронной почты. Используется для входа.
    phone (CharField): Номер телефона пользователя. Максимум 15 символов.
    city (CharField): Город проживания пользователя. Максимум 50 символов.
    chat_id (CharField): Номер пользователя в телеграмм
    avatar (ImageField): Аватар пользователя. Загружается в папку 'users/avatar'.
    """

    username = None

    email = models.EmailField(unique=True, verbose_name="Почта", help_text="Введите почту", blank=False, null=False)
    phone = models.CharField(max_length=15, verbose_name="Телефон", help_text="Введите номер телефона")
    city = models.CharField(max_length=50, verbose_name="Город")
    chat_id = models.CharField(max_length=50, verbose_name="ID номер чата в телеграм")
    avatar = models.ImageField(upload_to="users/avatar", verbose_name="Аватар")

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        """
        Определяет человекочитаемое имя модели и его множественную форму
        для отображения в интерфейсе администратора.
        """

        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
