from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from habits.models import Habits
from users.models import User


class HabitTestCase(APITestCase):

    def setUp(self):
        # Создаем пользователей
        self.user = User.objects.create(email="user@user.ru")
        self.user2 = User.objects.create(email="user2@user.ru")

        # Создаем полезную привычку с вознаграждением
        self.good_habit_with_reward = Habits.objects.create(
            user=self.user,
            place="Дом",
            time_success=90,
            action="Читать книгу",
            is_pleasant=False,
            fk_habits=None,
            period=1,
            reward="Чашка чая",
            max_time_processing=100,
            is_public=True,
        )

        # Создаем полезную привычку со связанной привычкой
        self.pleasant_habit_for_related = Habits.objects.create(
            user=self.user,
            place="Парк",
            time_success=60,
            action="Гулять",
            is_pleasant=True,
            fk_habits=None,
            period=1,
            reward="",
            max_time_processing=80,
            is_public=False,
        )

        self.good_habit_with_related = Habits.objects.create(
            user=self.user,
            place="Спортзал",
            time_success=120,
            action="Тренироваться",
            is_pleasant=False,
            fk_habits=self.pleasant_habit_for_related,
            period=7,
            reward="",
            max_time_processing=150,
            is_public=True,
        )

        # Создаем приятные привычки
        self.pleasant_habit = Habits.objects.create(
            user=self.user,
            place="Диван",
            time_success=30,
            action="Слушать музыку",
            is_pleasant=True,
            fk_habits=None,
            period=1,
            reward="",
            max_time_processing=50,
            is_public=False,
        )

        # Создаем привычки другого пользователя
        self.public_habit_user2 = Habits.objects.create(
            user=self.user2,
            place="Офис",
            time_success=45,
            action="Пить воду",
            is_pleasant=False,
            fk_habits=None,
            period=1,
            reward="Перерыв",
            max_time_processing=60,
            is_public=True,
        )

        self.private_habit_user2 = Habits.objects.create(
            user=self.user2,
            place="Спальня",
            time_success=20,
            action="Медитировать",
            is_pleasant=True,
            fk_habits=None,
            period=1,
            reward="",
            max_time_processing=30,
            is_public=False,
        )

        self.client.force_authenticate(user=self.user)

    def test_habit_create_good_habit_with_reward(self):
        """Тест создания полезной привычки с вознаграждением"""
        url = reverse("habits:habit-create")
        body = {
            "place": "Работа",
            "time_success": 90,
            "action": "Работать",
            "is_pleasant": False,
            "period": 1,
            "reward": "Кофе",
            "max_time_processing": 100,
            "is_public": True,
        }
        response = self.client.post(url, body, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Habits.objects.count(), 7)

        habit = Habits.objects.get(place="Работа")
        self.assertEqual(habit.reward, "Кофе")
        self.assertIsNone(habit.fk_habits)

    def test_habit_create_good_habit_with_related_habit(self):
        """Тест создания полезной привычки со связанной привычкой"""
        url = reverse("habits:habit-create")
        body = {
            "place": "Спальня",
            "time_success": 60,
            "action": "Читать",
            "is_pleasant": False,
            "fk_habits": self.pleasant_habit.id,
            "period": 7,
            "reward": "",
            "max_time_processing": 80,
            "is_public": False,
        }
        response = self.client.post(url, body, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Habits.objects.count(), 7)

        habit = Habits.objects.get(place="Спальня")
        self.assertEqual(habit.fk_habits, self.pleasant_habit)
        self.assertEqual(habit.reward, "")

    def test_habit_create_time_success_error(self):
        """Тест ошибки при превышении времени выполнения"""
        url = reverse("habits:habit-create")
        body = {
            "place": "Тест",
            "time_success": 150,
            "action": "Тест",
            "is_pleasant": False,
            "period": 1,
            "reward": "Тест",
            "max_time_processing": 160,
            "is_public": True,
        }
        response = self.client.post(url, body, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Время выполнения не должно превышать 120 секунд", str(response.content))

    def test_habit_create_related_habit_error(self):
        """Тест ошибки при выборе неправильной связанной привычки"""
        url = reverse("habits:habit-create")
        body = {
            "place": "Тест",
            "time_success": 90,
            "action": "Тест",
            "is_pleasant": False,
            "fk_habits": self.good_habit_with_reward.id,  # Не приятная привычка
            "period": 1,
            "reward": "",
            "max_time_processing": 100,
            "is_public": True,
        }
        response = self.client.post(url, body, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("В качестве связанной привычки можно выбрать только приятную привычку", str(response.content))

    def test_habit_create_reward_and_related_error(self):
        """Тест ошибки при одновременном выборе вознаграждения и связанной привычки"""
        url = reverse("habits:habit-create")
        body = {
            "place": "Тест",
            "time_success": 90,
            "action": "Тест",
            "is_pleasant": False,
            "fk_habits": self.pleasant_habit.id,
            "period": 1,
            "reward": "Тест",
            "max_time_processing": 100,
            "is_public": True,
        }
        response = self.client.post(url, body, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Нельзя одновременно выбирать и связанную привычку и вознаграждение", str(response.content))

    def test_habit_create_pleasant_habit_with_reward_error(self):
        """Тест ошибки при создании приятной привычки с вознаграждением"""
        url = reverse("habits:habit-create")
        body = {
            "place": "Тест",
            "time_success": 30,
            "action": "Тест",
            "is_pleasant": True,
            "period": 1,
            "reward": "Тест",
            "max_time_processing": 40,
            "is_public": False,
        }
        response = self.client.post(url, body, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Приятная привычка не может иметь вознаграждения", str(response.content))

    def test_habit_create_pleasant_habit_with_related_error(self):
        """Тест ошибки при создании приятной привычки со связанной привычкой"""
        url = reverse("habits:habit-create")
        body = {
            "place": "Тест",
            "time_success": 30,
            "action": "Тест",
            "is_pleasant": True,
            "fk_habits": self.pleasant_habit.id,
            "period": 1,
            "reward": "",
            "max_time_processing": 40,
            "is_public": False,
        }
        response = self.client.post(url, body, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Приятная привычка не может быть связана с другой привычкой", str(response.content))

    def test_habit_create_good_habit_no_reward_or_related_error(self):
        """Тест ошибки при создании полезной привычки без вознаграждения и связанной привычки"""
        url = reverse("habits:habit-create")
        body = {
            "place": "Тест",
            "time_success": 90,
            "action": "Тест",
            "is_pleasant": False,
            "period": 1,
            "reward": "",
            "max_time_processing": 100,
            "is_public": True,
        }
        response = self.client.post(url, body, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Полезная привычка должна иметь либо вознаграждение, либо связанную привычку",
                      str(response.content))

    def test_habit_create_pleasant_habit_success(self):
        """Тест успешного создания приятной привычки"""
        url = reverse("habits:habit-create")
        body = {
            "place": "Пляж",
            "time_success": 45,
            "action": "Загорать",
            "is_pleasant": True,
            "period": 1,
            "reward": "",
            "max_time_processing": 60,
            "is_public": False,
        }
        response = self.client.post(url, body, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Habits.objects.count(), 7)

        habit = Habits.objects.get(place="Пляж")
        self.assertTrue(habit.is_pleasant)
        self.assertEqual(habit.reward, "")

    def test_habit_retrieve_own_habit(self):
        """Тест получения своей привычки"""
        url = reverse("habits:habit-detail", args=(self.good_habit_with_reward.id,))
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['place'], "Дом")

    def test_habit_retrieve_public_habit_other_user(self):
        """Тест получения публичной привычки другого пользователя"""
        url = reverse("habits:habit-detail", args=(self.public_habit_user2.id,))
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['place'], "Офис")

    def test_habit_retrieve_private_habit_other_user_error(self):
        """Тест ошибки при получении приватной привычки другого пользователя"""
        url = reverse("habits:habit-detail", args=(self.private_habit_user2.id,))
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_habit_list_own_habits(self):
        """Тест получения списка своих привычек"""
        url = reverse("habits:habit-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Должны видеть 3 свои привычки
        self.assertEqual(len(response.data['results']), 4)  # 4 созданные + возможно пагинация

    def test_habit_update_own_habit(self):
        """Тест обновления своей привычки"""
        url = reverse("habits:habit-update", args=(self.good_habit_with_reward.id,))
        body = {
            "place": "Обновленное место",
            "reward": "Обновленное вознаграждение",
        }
        response = self.client.patch(url, body, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.good_habit_with_reward.refresh_from_db()
        self.assertEqual(self.good_habit_with_reward.place, "Обновленное место")
        self.assertEqual(self.good_habit_with_reward.reward, "Обновленное вознаграждение")

    def test_habit_update_other_user_habit_error(self):
        """Тест ошибки при обновлении чужой привычки"""
        url = reverse("habits:habit-update", args=(self.public_habit_user2.id,))
        body = {"place": "Попытка изменить"}
        response = self.client.patch(url, body, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_habit_delete_own_habit(self):
        """Тест удаления своей привычки"""
        url = reverse("habits:habit-delete", args=(self.good_habit_with_reward.id,))
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Habits.objects.count(), 5)

    def test_habit_delete_other_user_habit_error(self):
        """Тест ошибки при удалении чужой привычки"""
        url = reverse("habits:habit-delete", args=(self.public_habit_user2.id,))
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Habits.objects.count(), 6)

    def test_public_habit_list(self):
        """Тест получения списка публичных привычек"""
        url = reverse("habits:public-habit-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Должны видеть 2 публичные привычки (одна своя, одна другого пользователя)
        self.assertEqual(len(response.data), 2)