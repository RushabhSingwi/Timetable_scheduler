from datetime import timedelta

from django.db import models


class Teacher(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class ClassroomType(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class AvailabilityStatus(models.TextChoices):
    AVAILABLE = 'A', 'Available'
    NOT_AVAILABLE = 'N', 'Not Available'


class Classrooms(models.Model):
    classroom_type = models.ForeignKey(ClassroomType, on_delete=models.CASCADE)
    classroom_name = models.CharField(max_length=10, blank=False, null=False)

    # Availability for each hour slot (9 AM to 5 PM)
    slot_9_10 = models.CharField(max_length=1, choices=AvailabilityStatus.choices, default=AvailabilityStatus.AVAILABLE)
    slot_10_11 = models.CharField(max_length=1, choices=AvailabilityStatus.choices,
                                  default=AvailabilityStatus.AVAILABLE)
    slot_11_12 = models.CharField(max_length=1, choices=AvailabilityStatus.choices,
                                  default=AvailabilityStatus.AVAILABLE)
    slot_12_1 = models.CharField(max_length=1, choices=AvailabilityStatus.choices, default=AvailabilityStatus.AVAILABLE)
    slot_1_2 = models.CharField(max_length=1, choices=AvailabilityStatus.choices, default=AvailabilityStatus.AVAILABLE)
    slot_2_3 = models.CharField(max_length=1, choices=AvailabilityStatus.choices, default=AvailabilityStatus.AVAILABLE)
    slot_3_4 = models.CharField(max_length=1, choices=AvailabilityStatus.choices, default=AvailabilityStatus.AVAILABLE)
    slot_4_5 = models.CharField(max_length=1, choices=AvailabilityStatus.choices, default=AvailabilityStatus.AVAILABLE)

    def __str__(self):
        return f"{self.classroom_type.name} - {self.id}"

    def check_availability(self, hour):
        """
        Check if this specific classroom is available at a specific hour.
        """
        slot_name = f'slot_{hour}_{hour + 1}'  # e.g., 'slot_9_10'
        return getattr(self, slot_name) == AvailabilityStatus.AVAILABLE

    def book_classroom(self, hour):
        if hour < 9 or hour > 16:
            raise ValueError("Hour must be between 9 and 16 (inclusive).")

        slot_name = f'slot_{hour}_{hour + 1}'

        if not self.check_availability(hour):
            raise Exception(f"{self} is not available at {hour}:00.")

        # Mark the classroom as not available
        setattr(self, slot_name, 'N')  # Set to Not Available
        self.save()  # Save changes to the database


class Subject(models.Model):
    name = models.CharField(max_length=100)
    duration = models.IntegerField(default=1)
    classroom = models.ForeignKey(Classrooms, on_delete=models.CASCADE, default=1)
    subject_code = models.CharField(max_length=20, blank=False, null=False)

    def __str__(self):
        return self.name


class Class(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class ClassSubject(models.Model):
    class_name = models.ForeignKey(Class, on_delete=models.CASCADE, blank=False, null=False)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    number_of_lectures = models.IntegerField(blank=False, null=False)

    def __str__(self):
        return self.class_name.name + self.subject.name


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
    class_subject = models.ForeignKey(ClassSubject, on_delete=models.CASCADE, blank=False, null=False)
    day = models.IntegerField(blank=False, null=False)  # Representing days of the week as integers
    hour = models.IntegerField(blank=False, null=False)  # Representing hour in the 24-hour format
    # (9 = 9 AM, 10 = 10 AM, etc.)
    duration = models.DurationField(default=timedelta(hours=1))  # Duration of the lecture
