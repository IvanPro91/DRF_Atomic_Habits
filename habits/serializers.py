from rest_framework import serializers

from habits.models import Habits
from habits.validators import HabitValidator


class HabitsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Habits
        fields = "__all__"
        validators = [HabitValidator()]

    def to_internal_value(self, data):
        if self.instance:
            if not data.get("period"):
                data["period"] = [day.pk for day in self.instance.days_of_week.all()]
            for field in self.fields.keys():
                if field not in data.keys():
                    data[field] = getattr(self.instance, field)
        return data


class PublicHabitsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Habits
        fields = ("action", "is_pleasant", "max_time_processing")
