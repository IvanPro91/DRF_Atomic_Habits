import json

from django_celery_beat.models import CrontabSchedule, PeriodicTask

from habits.models import Habits


def create_replacements() -> dict[str, str]:
    """Создает словарь замен для формирования cron-расписания."""
    m = "0"
    h = "9"
    x = h
    y = "0"
    z = str((int(x) + int(y)) // 2) if y != "0" else x
    d = "*"

    return {"m": m, "x": x, "y": y, "z": z, "h": h, "d": d}


def make_replacements(text: str, replacements: dict) -> str:
    """Заменяет переменные в тексте на соответствующие значения."""
    for k, v in replacements.items():
        text = text.replace(k, v)
    return text


def create_schedule(crontab: str) -> CrontabSchedule:
    """Создает расписание для отправки напоминаний."""
    minute, hour, day_of_month, month_of_year, day_of_week = crontab.split()
    schedule, created = CrontabSchedule.objects.get_or_create(
        minute=minute,
        hour=hour,
        day_of_week=day_of_week,
        day_of_month=day_of_month,
        month_of_year=month_of_year,
    )
    return schedule


def create_periodic_task_for_habit(habit: Habits) -> None:
    """Создает периодическую задачу для отправки напоминаний о привычке."""
    # Определяем cron-расписание на основе периодичности привычки
    if habit.period == 1:  # Ежедневно
        crontab = "0 9 * * *"  # Каждый день в 9:00
    elif habit.period == 7:  # Еженедельно
        crontab = "0 9 * * 1"  # Каждый понедельник в 9:00
    elif habit.period == 30:  # Ежемесячно
        crontab = "0 9 1 * *"  # Первое число каждого месяца в 9:00
    else:
        crontab = "0 9 * * *"  # По умолчанию ежедневно

    schedule = create_schedule(crontab)

    # Создаем периодическую задачу
    PeriodicTask.objects.create(
        crontab=schedule,
        name=f"Напоминание о привычке {habit.pk} - {habit.action}",
        task="habits.tasks.send_habit_reminder",
        args=json.dumps([habit.pk]),
        description=f"Напоминание для привычки: {habit.action} в {habit.place}",
    )


def update_habit_schedule(habit: Habits) -> None:
    """Обновляет расписание для существующей привычки."""
    # Удаляем старые задачи для этой привычки
    PeriodicTask.objects.filter(name__startswith=f"Напоминание о привычке {habit.pk}").delete()

    # Создаем новую задачу
    create_periodic_task_for_habit(habit)


def delete_habit_schedule(habit_id: int) -> None:
    """Удаляет расписание для привычки."""
    PeriodicTask.objects.filter(name__startswith=f"Напоминание о привычке {habit_id}").delete()


def get_habit_crontab(period: int) -> str:
    """Возвращает cron-строку на основе периодичности привычки."""
    crontab_map = {
        1: "0 9 * * *",  # Ежедневно в 9:00
        7: "0 9 * * 1",  # Еженедельно в понедельник в 9:00
        30: "0 9 1 * *",  # Ежемесячно 1 числа в 9:00
    }
    return crontab_map.get(period, "0 9 * * *")


def create_task(schedule: CrontabSchedule, habit: Habits) -> None:
    """Creates period task to send reminders."""
    PeriodicTask.objects.create(
        crontab=schedule,
        name=f"Sending reminder {habit.pk}",
        task="habits.tasks.send_message",
        args=json.dumps([habit.pk]),
    )
