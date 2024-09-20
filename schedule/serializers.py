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

