from datetime import timedelta

from django.db import models


class Teacher(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Check if this is a new Teacher object (i.e., not already in the database)
        is_new = self._state.adding
        super(Teacher, self).save(*args, **kwargs)

        # If it's a new teacher, create Availability for each day
        if is_new:
            for day in range(1, 7):  # Assuming days 1 to 6 represent Monday to Saturday
                Availability.objects.create(
                    teacher=self,
                    day=day,
                    slot_9_10=AvailabilityStatus.AVAILABLE,
                    slot_10_11=AvailabilityStatus.AVAILABLE,
                    slot_11_12=AvailabilityStatus.AVAILABLE,
                    slot_12_1=AvailabilityStatus.AVAILABLE,
                    slot_1_2=AvailabilityStatus.AVAILABLE,
                    slot_2_3=AvailabilityStatus.AVAILABLE,
                    slot_3_4=AvailabilityStatus.AVAILABLE,
                    slot_4_5=AvailabilityStatus.AVAILABLE,
                )


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

    def __str__(self):
        return f"{self.classroom_name} - {self.id}"

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
    classroom_type = models.ForeignKey(ClassroomType, on_delete=models.CASCADE)
    subject_code = models.CharField(max_length=20, blank=False, null=False)

    def __str__(self):
        return self.subject_code+self.name


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


class Elective(models.Model):
    name = models.CharField(max_length=100, blank=False, null=False)
    subject_code = models.CharField(max_length=20, blank=False, null=False)
    class_pair = models.ManyToManyField(Class, related_name='electives')
    teacher_pair = models.ManyToManyField(Teacher, related_name='elective_teacher')
    duration = models.IntegerField(default=1)
    classroom_type = models.ForeignKey(ClassroomType, on_delete=models.CASCADE)
    number_of_lectures = models.IntegerField(blank=False, null=False)

    def __str__(self):
        return self.subject_code+self.name


class Schedule(models.Model):
    class_subject = models.ForeignKey(ClassSubject, on_delete=models.CASCADE, blank=True, null=True)
    day = models.IntegerField(blank=False, null=False)  # Representing days of the week as integers
    hour = models.IntegerField(blank=False, null=False)  # Representing hour in the 24-hour format
    # (9 = 9 AM, 10 = 10 AM, etc.)
    duration = models.DurationField(default=timedelta(hours=1))  # Duration of the lecture
    classroom = models.ForeignKey(Classrooms, on_delete=models.CASCADE, blank=True, null=True)  # New field
    class_object = models.ForeignKey(Class, on_delete=models.CASCADE, blank=True, null=True)
