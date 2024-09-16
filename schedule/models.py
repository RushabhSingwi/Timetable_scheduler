from django.db import models

class Teacher(models.Model):
    name = models.CharField(max_length=100)

class Subject(models.Model):
    name = models.CharField(max_length=100)

class Class(models.Model):
    name = models.CharField(max_length=100)
    subjects = models.ManyToManyField(Subject, through='ClassSubject')

class ClassSubject(models.Model):
    class_name = models.ForeignKey(Class, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    number_of_lectures = models.IntegerField()


class AvailabilityStatus(models.TextChoices):
    AVAILABLE = 'A', 'Available'
    NOT_AVAILABLE = 'N', 'Not Available'


class Availability(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    day = models.IntegerField()  # Representing days of the week as integers

    # Store availability for each hour as an enum
    slot_9_10 = models.CharField(max_length=1, choices=AvailabilityStatus.choices,
                                 default=AvailabilityStatus.AVAILABLE)
    slot_10_11 = models.CharField(max_length=1, choices=AvailabilityStatus.choices,
                                  default=AvailabilityStatus.AVAILABLE)
    slot_11_12 = models.CharField(max_length=1, choices=AvailabilityStatus.choices,
                                  default=AvailabilityStatus.AVAILABLE)
    slot_12_1 = models.CharField(max_length=1, choices=AvailabilityStatus.choices,
                                 default=AvailabilityStatus.AVAILABLE)
    slot_1_2 = models.CharField(max_length=1, choices=AvailabilityStatus.choices,
                                default=AvailabilityStatus.AVAILABLE)
    slot_2_3 = models.CharField(max_length=1, choices=AvailabilityStatus.choices,
                                default=AvailabilityStatus.AVAILABLE)
    slot_3_4 = models.CharField(max_length=1, choices=AvailabilityStatus.choices,
                                default=AvailabilityStatus.AVAILABLE)
    slot_4_5 = models.CharField(max_length=1, choices=AvailabilityStatus.choices,
                                default=AvailabilityStatus.AVAILABLE)


class Schedule(models.Model):
    class_subject = models.ForeignKey(ClassSubject, on_delete=models.CASCADE)
    day = models.IntegerField()  # Representing days of the week as integers
    hour = models.IntegerField()  # Representing hour in the 24-hour format (9 = 9 AM, 10 = 10 AM, etc.)
    duration = models.DurationField()  # Duration of the lecture
