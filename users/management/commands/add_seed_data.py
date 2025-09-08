import random
from datetime import datetime, timedelta

from django.contrib.auth import get_user_model
from django.core.management import BaseCommand
from django.utils import timezone
from lms.models import Course, Lesson

from users.models import Pay, User

User = get_user_model()


class Command(BaseCommand):
    help = "Очищает БД и засеивает тестовыми данными: пользователи, курсы, уроки, платежи"

    def handle(self, *args, **kwargs):
        self.stdout.write("Начало выполнения команды seed...")

        # --- Шаг 1: Очистка существующих данных ---
        self.stdout.write("Очистка данных...")

        models_to_clear = [Pay, Lesson, Course, User]
        for model in models_to_clear:
            count, _ = model.objects.all().delete()
            self.stdout.write(f"Удалено {count} записей из {model.__name__}")

        self.stdout.write("Очистка завершена\n")

        # --- Шаг 2: Создание пользователей ---
        self.stdout.write("Создание пользователей...")
        users_data = [
            {
                "email": "admin@admin.com",
                "is_staff": True,
                "is_active": True,
                "is_superuser": True,
                "password": "1234",
            },
            {
                "email": "moderator@site.com",
                "is_staff": True,
                "is_active": True,
                "is_superuser": False,
                "password": "1234",
            },
        ]

        created_users = []
        for data in users_data:
            user = User.objects.create(
                email=data["email"],
                is_staff=data["is_staff"],
                is_active=data["is_active"],
                is_superuser=data["is_superuser"],
            )
            user.set_password(data["password"])
            user.save()
            created_users.append(user)
            self.stdout.write(f"Создан: {user.email}")

        # Генерация 10 случайных студентов
        domains = ["example.com", "mail.ru", "test.org", "school.edu"]
        first_names = ["Alice", "Bob", "Charlie", "Diana", "Eve", "Frank", "Grace", "Henry"]
        last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis"]

        for i in range(10):
            fname = random.choice(first_names)
            lname = random.choice(last_names)
            domain = random.choice(domains)
            i += 1
            email = f"{fname.lower()}.{lname.lower()}{i}@{domain}"

            user = User.objects.create(
                email=email,
                is_staff=False,
                is_active=True,
                is_superuser=False,
            )
            user.set_password("123456")
            user.save()
            created_users.append(user)
            self.stdout.write(f"Создан студент: {email}")

        self.stdout.write(f"Всего создано пользователей: {len(created_users)}\n")

        # --- Шаг 3: Создание курсов ---
        self.stdout.write("Создание курсов...")
        course_names = [
            "Python для начинающих",
            "Django REST Framework",
            "JavaScript: основы",
            "React.js — от новичка к профи",
            "Базы данных: SQL и PostgreSQL",
            "Machine Learning с Python",
            "DevOps: Docker и Kubernetes",
            "Тестирование на Python",
        ]

        courses = []
        for name in course_names:
            course = Course.objects.create(name=name, description=f"Полное описание курса: {name}")
            courses.append(course)
            self.stdout.write(f"Курс создан: {course.name}")

        self.stdout.write(f"Всего курсов: {len(courses)}\n")

        # --- Шаг 4: Создание уроков ---
        self.stdout.write("Создание уроков...")
        lesson_topics = [
            "Переменные и типы данных",
            "Условные операторы",
            "Циклы",
            "Функции",
            "Классы и ООП",
            "Работа с файлами",
            "Исключения",
            "Модули и пакеты",
            "Работа с API",
            "Асинхронность",
        ]

        lessons = []
        for course in courses:
            num_lessons = random.randint(3, 6)
            for i in range(num_lessons):
                topic = random.choice(lesson_topics)
                i += 1
                lesson = Lesson(
                    name=f"Урок {i}: {topic}", description=f"Подробное изучение темы: {topic}", course=course
                )
                lessons.append(lesson)

        # Массовое создание уроков
        Lesson.objects.bulk_create(lessons, ignore_conflicts=True)

        # Перезагружаем уроки с id из БД (обязательно после bulk_create!)
        lessons = list(Lesson.objects.all())

        self.stdout.write(f"Создано уроков: {len(lessons)}\n")

        # --- Шаг 5: Создание платежей ---
        self.stdout.write("Создание платежей...")
        pay_types = [Pay.TYPE_CASH, Pay.TYPE_TRANSFER_ACCOUNT]

        start_date = timezone.make_aware(datetime(2023, 1, 1))
        end_date = timezone.now()

        pays = []
        for _ in range(50):
            user = random.choice(created_users)
            if user.is_superuser:
                continue

            # Выбираем: оплата за курс или за урок
            if random.choice([True, False]):
                course = random.choice(courses)
                lesson = None
            else:
                lesson = random.choice(lessons)
                course = None

            money = random.randint(1000, 100000)
            days_offset = random.randint(0, (end_date - start_date).days)
            pay_date = start_date + timedelta(days=days_offset)

            pays.append(
                Pay(
                    user=user,
                    course=course,
                    lesson=lesson,
                    money=money,
                    type_pay=random.choice(pay_types),
                    date_pay=pay_date,
                )
            )

        # Массовое создание платежей
        Pay.objects.bulk_create(pays)
        self.stdout.write(f"Создано платежей: {len(pays)}\n")

        # --- Финал ---
        self.stdout.write(self.style.SUCCESS("Засеивание базы данных завершено успешно!"))
