from datetime import timedelta
from django.test import TestCase
from ..models import Teacher, Class, Schedule, ClassSubject, Subject, Classrooms, ClassroomType
from ..serializers import (
    TeacherSerializer, SubjectSerializer, ClassSerializer,
    ClassSubjectSerializer, ScheduleSerializer, BookSlotSerializer,
    ClassroomTypeSerializer, ClassroomsSerializer, ClassroomBookingSerializer
)


class TeacherSerializerTestCase(TestCase):
    def test_teacher_serialization(self):
        teacher = Teacher.objects.create(name="John Doe")
        serializer = TeacherSerializer(teacher)
        self.assertEqual(serializer.data, {'id': teacher.id, 'name': 'John Doe'})


class SubjectSerializerTestCase(TestCase):
    def test_subject_serialization(self):
        subject = Subject.objects.create(name="Math", duration=2)
        serializer = SubjectSerializer(subject)
        self.assertEqual(serializer.data, {'id': subject.id, 'name': 'Math', 'duration': 2})


class ClassSerializerTestCase(TestCase):
    def test_class_serialization(self):
        class_instance = Class.objects.create(name="10A")
        serializer = ClassSerializer(class_instance)
        self.assertEqual(serializer.data, {'id': class_instance.id, 'name': '10A'})


class ClassSubjectSerializerTestCase(TestCase):
    def test_class_subject_serialization(self):
        teacher = Teacher.objects.create(name="John Doe")
        class_instance = Class.objects.create(name="10A")
        subject = Subject.objects.create(name="Math", duration=2)
        class_subject = ClassSubject.objects.create(
            class_name=class_instance, subject=subject, teacher=teacher, number_of_lectures=3)
        serializer = ClassSubjectSerializer(class_subject)
        self.assertEqual(serializer.data, {
            'class_name': class_subject.class_name.id,
            'subject': class_subject.subject.id,
            'teacher': class_subject.teacher.id,
            'number_of_lectures': 3
        })


class ScheduleSerializerTestCase(TestCase):
    def test_schedule_serialization(self):
        teacher = Teacher.objects.create(name="John Doe")
        class_instance = Class.objects.create(name="10A")
        schedule = Schedule.objects.create(
            teacher=teacher, class_name=class_instance, day=1, time=10)
        serializer = ScheduleSerializer(schedule)
        self.assertEqual(serializer.data, {
            'id': schedule.id,
            'teacher': {'id': teacher.id, 'name': teacher.name},
            'class_name': {'id': class_instance.id, 'name': class_instance.name},
            'day': 1,
            'time': 10
        })


class BookSlotSerializerTestCase(TestCase):
    def test_book_slot_serialization(self):
        # Create a ClassroomType first
        classroom_type = ClassroomType.objects.create(name="Lecture Hall")

        # Now create the Subject with the required classroom_type
        subject = Subject.objects.create(name="Math", duration=2, classroom_type=classroom_type)

        class_instance = Class.objects.create(name="Class A")
        teacher = Teacher.objects.create(name="Mr. Smith")
        class_subject = ClassSubject.objects.create(
            class_name=class_instance,
            subject=subject,
            teacher=teacher,
            number_of_lectures=3
        )

        data = {
            'day': 1,
            'time': 2,
            'class_subject_id': class_subject.id,
            'duration': 2
        }

        serializer = BookSlotSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        schedule = serializer.save()

        self.assertEqual(schedule.class_subject, class_subject)
        self.assertEqual(schedule.day, data['day'])
        self.assertEqual(schedule.hour, data['time'] + 9)  # Time is an index from 0-7 mapping to hours (9-17)
        self.assertEqual(schedule.duration, timedelta(hours=data['duration']))


class ClassroomTypeSerializerTestCase(TestCase):
    def test_classroom_type_serialization(self):
        classroom_type = ClassroomType.objects.create(name="Lab")
        serializer = ClassroomTypeSerializer(classroom_type)
        self.assertEqual(serializer.data, {'id': classroom_type.id, 'name': 'Lab'})


class ClassroomsSerializerTestCase(TestCase):
    def test_classrooms_serialization(self):
        classroom_type = ClassroomType.objects.create(name="Lab")
        classroom = Classrooms.objects.create(classroom_type=classroom_type)
        serializer = ClassroomsSerializer(classroom)
        self.assertEqual(serializer.data, {'id': classroom.id, 'classroom_type': classroom_type.id})


class ClassroomBookingSerializerTestCase(TestCase):
    def test_classroom_booking_hour_validation(self):
        data = {'classroom_id': 1, 'hour': 17}
        serializer = ClassroomBookingSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(serializer.errors['hour'], ['Hour must be between 9 and 16 (inclusive).'])

        valid_data = {'classroom_id': 1, 'hour': 10}
        valid_serializer = ClassroomBookingSerializer(data=valid_data)
        self.assertTrue(valid_serializer.is_valid())
