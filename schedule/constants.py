from django.db import models


class AvailabilityStatus(models.TextChoices):
    AVAILABLE = 'A', 'Available'
    NOT_AVAILABLE = 'N', 'Not Available'


class DayOfWeek(models.IntegerChoices):
    MONDAY = 1, 'Monday'
    TUESDAY = 2, 'Tuesday'
    WEDNESDAY = 3, 'Wednesday'
    THURSDAY = 4, 'Thursday'
    FRIDAY = 5, 'Friday'
    SATURDAY = 6, 'Saturday'
