from rest_framework import serializers
from .models import Teacher, Class, Schedule

class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = ['id', 'name']

class ClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = Class
        fields = ['id', 'name']

class ScheduleSerializer(serializers.ModelSerializer):
    teacher = TeacherSerializer()
    class_name = ClassSerializer()

    class Meta:
        model = Schedule
        fields = ['id', 'teacher', 'class_name', 'day', 'time']

class ScheduleInputSerializer(serializers.Serializer):
    num_days = serializers.IntegerField(min_value=1, max_value=7)
    classes = serializers.DictField(
        child=serializers.DictField(child=serializers.IntegerField(min_value=1))
    )