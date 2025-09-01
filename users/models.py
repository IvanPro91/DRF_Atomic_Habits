from django.contrib.auth.models import AbstractUser
from django.db import models

from lms.models import Course, Lesson


class User(AbstractUser):
    """
    Кастомная модель пользователя, заменяющая стандартную модель.

    Вместо поля `username` используется `email` как уникальный идентификатор
    для аутентификации. Позволяет хранить дополнительную информацию о пользователе:
    телефон, город, аватар.

    email (EmailField): Уникальный адрес электронной почты. Используется для входа.
    phone (CharField): Номер телефона пользователя. Максимум 15 символов.
    city (CharField): Город проживания пользователя. Максимум 50 символов.
    avatar (ImageField): Аватар пользователя. Загружается в папку 'users/avatar'.
    """

    username = None

    email = models.EmailField(unique=True, verbose_name="Почта", help_text="Введите почту", blank=False, null=False)
    phone = models.CharField(max_length=15, verbose_name="Телефон", help_text="Введите номер телефона")
    city = models.CharField(max_length=50, verbose_name="Город")
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


class Pay(models.Model):
    """
    Модель для хранения информации об оплатах пользователей за курсы или уроки.

    Платеж может быть связан либо с конкретным уроком, либо с курсом.
    Поддерживает два типа оплаты: наличные и безналичный перевод.

    user (ForeignKey): Ссылка на пользователя, совершившего оплату.
    date_pay (DateField): Дата совершения оплаты. Автоматически устанавливается при создании.
    lesson (ForeignKey): Ссылка на урок, за который произведена оплата. Необязательное поле.
    course (ForeignKey): Ссылка на курс, за который произведена оплата. Необязательное поле.
    money (PositiveIntegerField): Сумма оплаты в рублях (или другой валюте). По умолчанию 0.
    type_pay (CharField): Тип оплаты — наличные или безналичный расчёт.
        Выбор ограничен константами TYPE_CASH и TYPE_TRANSFER_ACCOUNT.
    """

    TYPE_CASH = "cash"
    TYPE_TRANSFER_ACCOUNT = "non_cash"

    STATUS_CHOICES = [
        (TYPE_CASH, "Наличные"),
        (TYPE_TRANSFER_ACCOUNT, "Перевод на счет"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь", null=True)
    date_pay = models.DateTimeField(auto_now=True, verbose_name="Дата оплаты")
    session_id = models.TextField(verbose_name="ИД сессии", null=True, blank=True)
    link = models.TextField(verbose_name="Ссылка на оплату", null=True, blank=True)
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name="payments",
        verbose_name="Оплаченный урок",
        null=True,
        blank=True,
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="payments",
        verbose_name="Оплаченный курс",
        null=True,
        blank=True,
    )
    money = models.PositiveIntegerField(default=0, verbose_name="Сумма оплаты")
    type_pay = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        verbose_name="Вид оплаты",
    )

    class Meta:
        """
        Определяет человекочитаемое имя модели и его множественную форму
        для отображения в интерфейсе администратора.
        """

        verbose_name = "Платеж"
        verbose_name_plural = "Платежи"

    def __str__(self):
        """Возвращает строковое представление объекта Pay."""
        return f"Платеж от {self.user.email} на сумму {self.money} руб."


class SubscribeUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name="Подписка на курс")

    class Meta:
        """
        Определяет человекочитаемое имя модели и его множественную форму
        для отображения в интерфейсе администратора.
        """

        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"

    def __str__(self):
        """Возвращает строковое представление объекта SubscribeUser."""
        return f"{self.user.name} -> подписка на {self.course.name}"
