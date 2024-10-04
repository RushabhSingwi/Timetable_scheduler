import random
from datetime import timedelta
from typing import List, Tuple

from django.db.models import Q

from .models import Availability, AvailabilityStatus, ClassSubject, Teacher, Schedule, Classrooms


class SchedulingService:
    def __init__(self, num_days: int = 6):
        self.num_days = num_days
        self.time_slots = 8  # 9 AM to 5 PM, 1-hour slots
        self.teachers = {}
        self.classes = {}
        self.schedule = []
        print("DEBUG: TimetableGenerator initialized")

    def prepare_data(self):
        print("DEBUG: Preparing data")
        # Fetch all ClassSubject entries
        class_subjects = ClassSubject.objects.all()

        # Prepare data structures
        for cs in class_subjects:
            if cs.class_name.name not in self.classes:
                self.classes[cs.class_name.name] = {}
            if cs.teacher.name not in self.classes[cs.class_name.name]:
                self.classes[cs.class_name.name][cs.teacher.name] = []
            self.classes[cs.class_name.name][cs.teacher.name].append(cs)

        print(f"DEBUG: Prepared data - Classes: {self.classes}, Teachers: {self.teachers}")

    def is_slot_available(self, day: int, time: int, teacher: str, class_name: str, classroom: Classrooms) -> bool:
        print(f"DEBUG: Checking availability for day {day}, time {time}, teacher {teacher}, class {class_name}")
        # Check teacher availability
        try:
            teacher_obj = Teacher.objects.get(name=teacher)
            availability = Availability.objects.get(teacher=teacher_obj, day=day)
            slot_field = f'slot_{time + 9}_{time + 10}'
            if getattr(availability, slot_field) == AvailabilityStatus.NOT_AVAILABLE:
                print(f"DEBUG: Teacher {teacher} not available")
                return False
        except (Teacher.DoesNotExist, Availability.DoesNotExist):
            print(f"DEBUG: No availability data for teacher {teacher}")
            # If no availability is defined, assume the teacher is available
            pass

            # Check classroom availability
            if not classroom.check_availability(time + 9):
                print(f"DEBUG: Classroom {classroom} not available")
                return False

        # Check if the slot is already booked
        existing_schedule = Schedule.objects.filter(
            Q(class_subject__teacher__name=teacher) | Q(class_subject__class_name__name=class_name),
            day=day,
            hour=time + 9
        )
        if existing_schedule.exists():
            print(f"DEBUG: Slot already booked")
            return False

        print(f"DEBUG: Slot is available")
        return True

    def book_slot(self, day: int, time: int, class_subject: ClassSubject, duration: int, classroom: Classrooms):
        print(f"DEBUG: Booking slot for day {day}, time {time}, class subject {class_subject}")
        # Loop to book consecutive time slots based on duration
        for slot_offset in range(duration):
            Schedule.objects.create(
                class_subject=class_subject,
                day=day,
                hour=(time + slot_offset) + 9,  # Adjust to the actual time format
                duration=timedelta(hours=1),  # Each slot is booked for 1 hour
                classroom=classroom
            )
            classroom.book_classroom((time + slot_offset) + 9)

    def has_teacher_scheduled_class(self, day: int, teacher: str, class_name: str) -> bool:
        print(f"DEBUG: Checking if teacher {teacher} is already scheduled for class {class_name} on day {day}")
        exists = Schedule.objects.filter(
            class_subject__teacher__name=teacher,
            class_subject__class_name__name=class_name,
            day=day
        ).exists()
        print(f"DEBUG: Teacher already scheduled: {exists}")
        return exists

    def generate_timetable(self):
        print("DEBUG: Starting timetable generation")
        self.prepare_data()

        for class_name, teachers in self.classes.items():
            for teacher, class_subjects in teachers.items():
                print(f"DEBUG: Scheduling for class {class_name}, teacher {teacher}, {len(class_subjects)} subjects")

                for class_subject in class_subjects:
                    subject_duration = class_subject.subject.duration
                    required_classroom_type = class_subject.subject.classroom_type
                    lectures_to_schedule = class_subject.number_of_lectures

                    lectures_scheduled = 0
                    attempts = 0
                    max_attempts = 100  # Prevent infinite loop
                    while lectures_scheduled < lectures_to_schedule and attempts < max_attempts:
                        day = random.randint(0, self.num_days - 1)
                        time = random.randint(0, self.time_slots - 1)

                        # Get available classrooms of the required type
                        available_classrooms = Classrooms.objects.filter(classroom_type=required_classroom_type)

                        for classroom in available_classrooms:
                            slots_available = True
                            for slot_offset in range(subject_duration):
                                if (time + slot_offset >= self.time_slots or
                                        not self.is_slot_available(day, time + slot_offset,
                                                                   teacher, class_name, classroom)):
                                    slots_available = False
                                    break

                            if slots_available and not self.has_teacher_scheduled_class(day, teacher, class_name):
                                self.book_slot(day, time, class_subject, subject_duration, classroom)
                                lectures_scheduled += 1
                                print(
                                    f"DEBUG: Scheduled {subject_duration}-hour lecture {lectures_scheduled}"
                                    f" for {class_name} with {teacher} in {classroom}")
                                break

                        attempts += 1

                    if lectures_scheduled < lectures_to_schedule:
                        print(
                            f"WARNING: Could not schedule all lectures for {class_name} with {teacher}."
                            f" Scheduled {lectures_scheduled}/{lectures_to_schedule}")

        print("DEBUG: Timetable generation complete")
        return self.get_schedule()

    def get_schedule(self) -> List[List[List[Tuple[str, str, str, str]]]]:
        print("DEBUG: Fetching schedule from database")
        schedule: List[List[List[Tuple[str, str, str, str]]]] = [[[] for _ in range(self.time_slots)] for _ in
                                                                 range(self.num_days)]

        for entry in Schedule.objects.all():
            day = entry.day
            time = entry.hour - 9  # Convert back to 0-based index
            class_name = entry.class_subject.class_name.name
            subject = entry.class_subject.subject.name
            teacher = entry.class_subject.teacher.name
            classroom = entry.classroom.classroom_name

            schedule[day][time].append((class_name, subject, teacher, classroom))

        print(f"DEBUG: Schedule Prepares")
        print(f"Use print_timetable method to print the timetable")
        return schedule

    def print_timetable(self):
        print("DEBUG: Printing timetable")
        schedule = self.get_schedule()
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
        times = ['9-10', '10-11', '11-12', '12-1', '1-2', '2-3', '3-4', '4-5']

        # Dictionary to hold class schedules
        class_schedules = {}

        # Populate the class schedules
        for day_index, day_schedule in enumerate(schedule):
            for time_index, slots in enumerate(day_schedule):
                for class_name, subject, teacher in slots:
                    if class_name not in class_schedules:
                        class_schedules[class_name] = [["Free" for _ in times] for _ in days]
                    class_schedules[class_name][day_index][time_index] = f"{subject} - {teacher}"

        # Print timetable for each class
        for class_name, timetable in class_schedules.items():
            print(f"\nTimetable for {class_name}:")
            print("                ", end="")
            print(" | ".join(times))  # Print time slots header
            print("-" * (len(times) * 16))  # Print a separator line

            for day_index, day in enumerate(days):
                print(f"{day:8} | ", end="")  # Print day header
                print(" | ".join(timetable[day_index]))  # Print each day's timetable
