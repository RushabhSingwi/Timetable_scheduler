from rest_framework import serializers
from .models import Teacher, Class, Schedule, ClassSubject


class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = ['id', 'name']

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


class ScheduleInputSerializer(serializers.Serializer):
    teachers = serializers.ListField(
        child=serializers.DictField(
            child=serializers.DictField()
        )
    )

    def validate_teachers(self, value):
        # Custom validation logic for teacher input if needed
        for teacher_data in value:
            if 'teacher_id' not in teacher_data or 'class_id' not in teacher_data or 'lectures_per_week' not in teacher_data:
                raise serializers.ValidationError(
                    "Each teacher must have 'teacher_id', 'class_id', and 'lectures_per_week'")
            if teacher_data['lectures_per_week'] <= 0:
                raise serializers.ValidationError("Number of lectures per week must be a positive integer.")
        return value

    def create(self, validated_data):
        teachers_data = validated_data['teachers']

        # Loop through each teacher data to create schedules
        for teacher_data in teachers_data:
            teacher = Teacher.objects.get(id=teacher_data['teacher_id'])
            class_instance = Class.objects.get(id=teacher_data['class_id'])
            lectures_per_week = teacher_data['lectures_per_week']

            # Create schedule records for each teacher and class
            for i in range(lectures_per_week):
                Schedule.objects.create(
                    teacher=teacher,
                    class_name=class_instance,
                    day=f'Day {i + 1}',  # Example: Create sequential days, you might replace this logic
                    time='10:00 AM'  # Example: Placeholder time, replace with your logic
                )

        return validated_data