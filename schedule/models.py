from datetime import timedelta

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from .constants import AvailabilityStatus, DayOfWeek


class Teacher(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    def is_available(self, day: int, time: int) -> bool:
        try:
            availability = self.availabilities.get(day=day)
            slot_field = f'slot_{time}_{time + 1}'
            return getattr(availability, slot_field) == AvailabilityStatus.AVAILABLE
        except TeacherAvailability.DoesNotExist:
            return False


class TeacherAvailability(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='availabilities')
    day = models.IntegerField(choices=DayOfWeek.choices)
    slot_9_10 = models.CharField(max_length=1, choices=AvailabilityStatus.choices, default=AvailabilityStatus.AVAILABLE)
    slot_10_11 = models.CharField(max_length=1, choices=AvailabilityStatus.choices,
                                  default=AvailabilityStatus.AVAILABLE)
    slot_11_12 = models.CharField(max_length=1, choices=AvailabilityStatus.choices,
                                  default=AvailabilityStatus.AVAILABLE)
    slot_12_13 = models.CharField(max_length=1, choices=AvailabilityStatus.choices,
                                  default=AvailabilityStatus.AVAILABLE)
    slot_13_14 = models.CharField(max_length=1, choices=AvailabilityStatus.choices,
                                  default=AvailabilityStatus.AVAILABLE)
    slot_14_15 = models.CharField(max_length=1, choices=AvailabilityStatus.choices,
                                  default=AvailabilityStatus.AVAILABLE)
    slot_15_16 = models.CharField(max_length=1, choices=AvailabilityStatus.choices,
                                  default=AvailabilityStatus.AVAILABLE)
    slot_16_17 = models.CharField(max_length=1, choices=AvailabilityStatus.choices,
                                  default=AvailabilityStatus.AVAILABLE)

    class Meta:
        unique_together = ('teacher', 'day')

    def __str__(self):
        return f"{self.teacher.name}'s availability on {self.get_day_display()}"


@receiver(post_save, sender=Teacher)
def create_teacher_availability(sender, instance, created, **kwargs):
    if created:
        for day in DayOfWeek:
            TeacherAvailability.objects.create(teacher=instance, day=day)


class ClassroomType(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Classrooms(models.Model):
    classroom_type = models.ForeignKey('ClassroomType', on_delete=models.CASCADE)
    classroom_name = models.CharField(max_length=10, blank=False, null=False)

    def __str__(self):
        return f"{self.classroom_name} - {self.id}"

    def is_classroom_available(self, day, time):
        """
        Check if this classroom is available at a specific day and time.
        :param day: Integer representing the day (e.g., 1 for Monday)
        :param time: Offset from 9 AM (e.g., 0 for 9 AM, 1 for 10 AM)
        :return: True if available, False otherwise
        """
        hour = time + 9  # Convert offset to the actual hour (0 -> 9 AM, 1 -> 10 AM)

        if hour < 9 or hour > 16:
            raise ValueError("Hour must be between 9 and 16.")

        # Fetch availability for this classroom and day
        try:
            availability = ClassroomAvailability.objects.get(classroom=self, day=day)
        except ClassroomAvailability.DoesNotExist:
            print(f"DEBUG: No availability record for {self} on day {day}.")
            return False

        # Dynamically check the relevant time slot (e.g., 'slot_9_10')
        slot_name = f'slot_{hour}_{hour + 1}'
        return getattr(availability, slot_name) == 'A'  # 'A' stands for Available

    def book_classroom(self, day, time):
        """
        Book the classroom at a specific day and time.
        :param day: Integer representing the day (e.g., 0 for Monday)
        :param time: Offset from 9 AM (e.g., 0 for 9 AM, 1 for 10 AM)
        """
        hour = time + 9
        if hour < 9 or hour > 16:
            raise ValueError("Hour must be between 9 and 16.")

        try:
            availability = ClassroomAvailability.objects.get(classroom=self, day=day)
        except ClassroomAvailability.DoesNotExist:
            raise Exception(f"No availability record found for {self} on day {day}.")

        slot_name = f'slot_{hour}_{hour + 1}'
        if getattr(availability, slot_name) != 'A':
            raise Exception(f"{self} is not available at {hour}:00 on day {day}.")

        # Book the classroom by setting the slot to 'N' (Not Available)
        setattr(availability, slot_name, 'N')
        availability.save()  # Save the updated availability

        print(f"DEBUG: {self} booked successfully at {hour}:00 on day {day}.")


class ClassroomAvailability(models.Model):
    classroom = models.ForeignKey(Classrooms, on_delete=models.CASCADE, related_name='availabilities')
    day = models.IntegerField(choices=DayOfWeek.choices)

    # Hour slots for 9 AM to 5 PM
    slot_9_10 = models.CharField(max_length=1, choices=AvailabilityStatus.choices,
                                 default=AvailabilityStatus.AVAILABLE)
    slot_10_11 = models.CharField(max_length=1, choices=AvailabilityStatus.choices,
                                  default=AvailabilityStatus.AVAILABLE)
    slot_11_12 = models.CharField(max_length=1, choices=AvailabilityStatus.choices,
                                  default=AvailabilityStatus.AVAILABLE)
    slot_12_13 = models.CharField(max_length=1, choices=AvailabilityStatus.choices,
                                  default=AvailabilityStatus.AVAILABLE)
    slot_13_14 = models.CharField(max_length=1, choices=AvailabilityStatus.choices,
                                  default=AvailabilityStatus.AVAILABLE)
    slot_14_15 = models.CharField(max_length=1, choices=AvailabilityStatus.choices,
                                  default=AvailabilityStatus.AVAILABLE)
    slot_15_16 = models.CharField(max_length=1, choices=AvailabilityStatus.choices,
                                  default=AvailabilityStatus.AVAILABLE)
    slot_16_17 = models.CharField(max_length=1, choices=AvailabilityStatus.choices,
                                  default=AvailabilityStatus.AVAILABLE)

    class Meta:
        unique_together = ('classroom', 'day')

    def __str__(self):
        return f"Availability for {self.classroom} on day {self.day}"

    def check_slot(self, hour):
        slot_name = f'slot_{hour}_{hour + 1}'
        return getattr(self, slot_name) == AvailabilityStatus.AVAILABLE

    def book_slot(self, hour):
        slot_name = f'slot_{hour}_{hour + 1}'

        if not self.check_slot(hour):
            raise Exception(f"{self.classroom} is not available at {hour}:00 on day {self.day}.")

        setattr(self, slot_name, 'N')  # Set to Not Available
        self.save()


class Subject(models.Model):
    name = models.CharField(max_length=100)
    duration = models.IntegerField(default=1)
    classroom_type = models.ForeignKey(ClassroomType, on_delete=models.CASCADE)
    subject_code = models.CharField(max_length=20, blank=False, null=False)

    def __str__(self):
        return self.subject_code + self.name


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


class Elective(models.Model):
    name = models.CharField(max_length=100, blank=False, null=False)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    class_pair = models.ManyToManyField(Class, related_name='electives')
    teacher_pair = models.ManyToManyField(Teacher, related_name='elective_teacher')
    duration = models.IntegerField(default=1)
    number_of_lectures = models.IntegerField(blank=False, null=False)

    def __str__(self):
        return self.subject.subject_code + self.name


class ClassSchedule(models.Model):
    class_subject = models.ForeignKey(ClassSubject, on_delete=models.CASCADE, blank=True, null=True)
    day = models.IntegerField(blank=False, null=False)  # Representing days of the week as integers
    hour = models.IntegerField(blank=False, null=False)  # Representing hour in the 24-hour format
    # (9 = 9 AM, 10 = 10 AM, etc.)
    duration = models.DurationField(default=timedelta(hours=1))  # Duration of the lecture
    classroom = models.ForeignKey(Classrooms, on_delete=models.CASCADE, blank=True, null=True)  # New field
    class_object = models.ForeignKey(Class, on_delete=models.CASCADE, blank=True, null=True)


class TeacherSchedule(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    day = models.IntegerField(choices=DayOfWeek.choices)
    hour = models.IntegerField()  # Representing hour in the 24-hour format
    duration = models.DurationField(default=timedelta(hours=1))  # Duration of the lecture
    classroom = models.ForeignKey('Classrooms', on_delete=models.CASCADE, blank=True, null=True)
    class_object = models.ForeignKey('Class', on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return f"{self.teacher.name}'s schedule on {self.get_day_display()} at {self.hour}:00"
