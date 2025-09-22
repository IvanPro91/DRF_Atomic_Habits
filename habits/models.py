from django.db import models

from users.models import User


class Habits(models.Model):
    # Периодичность выполнения привычки
    DAILY = 1
    WEEKLY = 7
    MONTHLY = 30

    PERIOD_CHOICES = [
        (DAILY, "Ежедневно"),
        (WEEKLY, "Еженедельно"),
        (MONTHLY, "Ежемесячно"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь", related_name="habits")
    place = models.CharField(max_length=255, verbose_name="Место")
    time_success = models.PositiveIntegerField(
        verbose_name="Время выполнения (сек)", default=120, help_text="Время на выполнение привычки в секундах"
    )
    action = models.CharField(max_length=500, verbose_name="Действие")
    is_pleasant = models.BooleanField(verbose_name="Признак приятной привычки", default=False)
    related_habit = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        verbose_name="Связанная привычка",
        null=True,
        blank=True,
        related_name="linked_habits",
    )
    period = models.PositiveIntegerField(
        verbose_name="Частота выполнения привычки",
        default=DAILY,
        choices=PERIOD_CHOICES,
        help_text="Периодичность выполнения привычки",
    )
    reward = models.CharField(max_length=500, verbose_name="Вознаграждение", blank=True, null=True)
    max_time_processing = models.PositiveIntegerField(
        verbose_name="Максимальное время выполнения (сек)",
        default=120,
        help_text="Максимальное время на выполнение в секундах",
    )
    is_public = models.BooleanField(verbose_name="Признак публичности", default=False)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    def __str__(self):
        return f"{self.action} в {self.place}"

    class Meta:
        verbose_name = "Привычка"
        verbose_name_plural = "Привычки"
        ordering = ["-created_at"]
