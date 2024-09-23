from datetime import timedelta

from rest_framework import serializers
from .models import Teacher, Class, Schedule, ClassSubject, Subject


class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = ['id', 'name']


# Subject serializer
class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['id', 'name']


# Class serializer
class ClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = Class
        fields = ['id', 'name']


class ClassSubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassSubject
        fields = ['class_name', 'subject', 'teacher', 'number_of_lectures']


class ScheduleSerializer(serializers.ModelSerializer):
    teacher = TeacherSerializer()
    class_name = ClassSerializer()

    class Meta:
        model = Schedule
        fields = ['id', 'teacher', 'class_name', 'day', 'time']


class BookSlotSerializer(serializers.Serializer):
    day = serializers.IntegerField()
    time = serializers.IntegerField()
    class_subject_id = serializers.PrimaryKeyRelatedField(queryset=ClassSubject.objects.all())
    duration = serializers.IntegerField(default=1)  # Default duration is 1 hour

    def create(self, validated_data):
        class_subject = validated_data['class_subject_id']
        day = validated_data['day']
        time = validated_data['time']
        duration = validated_data.get('duration', 1)

        schedule = Schedule.objects.create(
            class_subject=class_subject,
            day=day,
            hour=time + 9,  # Assuming time is provided as an index (0-7) and maps to actual hours (9-17)
            duration=timedelta(hours=duration)
        )
        return schedule
