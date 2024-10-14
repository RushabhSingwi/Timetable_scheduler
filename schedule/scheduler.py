import random
from datetime import timedelta
from typing import List, Tuple, Optional

from .models import (AvailabilityStatus, ClassSubject, Teacher, Classrooms,
                     Class, Elective, ClassSchedule, TeacherSchedule, TeacherAvailability)


def book_class_slot(day: int, time: int, class_subject: Optional[ClassSubject], duration: int,
                    classroom: Optional[Classrooms], class_name: str):
    # Retrieve the class instance based on class_name (assuming 'Class' model is being used)
    try:
        class_instance = Class.objects.get(name=class_name)  # Adjust to the actual model name and field
    except Class.DoesNotExist:
        print(f"ERROR: Class with name {class_name} does not exist")
        return

    # Loop to book consecutive time slots based on duration
    for slot_offset in range(duration):
        # Handle booking either a class subject or a recess (if class_subject is None)
        if class_subject:
            ClassSchedule.objects.create(
                class_subject=class_subject,
                day=day,
                hour=(time + slot_offset) + 9,  # Adjust to the actual time format
                duration=timedelta(hours=1),  # Each slot is booked for 1 hour
                classroom=classroom,
                class_object=class_instance
            )
        else:
            ClassSchedule.objects.create(
                class_subject=None,
                day=day,
                hour=(time + slot_offset) + 9,  # Adjust to the actual time format
                duration=timedelta(hours=1),
                classroom=None,  # No classroom for recess
                # Optionally, you could store the class name if needed for identification
                class_object=class_instance
            )

        # Book classroom only if not recess
        if classroom and class_subject:
            classroom.book_classroom((time + slot_offset) + 9)


def book_teacher_slot(day: int, time: int, duration: int, teacher: Teacher,
                      classroom: Optional[Classrooms], class_name: str):
    try:
        class_instance = Class.objects.get(name=class_name)  # Adjust to the actual model name and field
    except Class.DoesNotExist:
        print(f"ERROR: Class with name {class_name} does not exist")
        return

    # Loop to book consecutive time slots based on duration
    for slot_offset in range(duration):
        TeacherSchedule.objects.create(
            teacher=teacher,
            day=day,
            hour=(time + slot_offset) + 9,  # Adjust to the actual time format
            duration=timedelta(hours=1),  # Each slot is booked for 1 hour
            classroom=classroom,
            class_object=class_instance
        )


def has_teacher_scheduled_class(day: int, teacher: str, class_name: str) -> bool:
    print(f"DEBUG: Checking if teacher {teacher} is already scheduled for class {class_name} on day {day}")

    # Fetch the teacher instance
    try:
        teacher_instance = Teacher.objects.get(name=teacher)
    except Teacher.DoesNotExist:
        print(f"DEBUG: Teacher {teacher} does not exist")
        return False

    exists = TeacherSchedule.objects.filter(
        teacher=teacher_instance,
        class_object__name=class_name,
        day=day
    ).exists()
    print(f"DEBUG: Teacher already scheduled: {exists}")
    return exists


class SchedulingService:
    def __init__(self, num_days: int = 6):
        self.num_days = num_days
        self.time_slots = 8  # 9 AM to 5 PM, 1-hour slots
        self.teachers = {}
        self.classes = {}
        self.schedule = []
        self.potential_recess_slots = [2, 3, 4]  # 11 AM, 12 PM, 1 PM (0-based index)
        self.chosen_recess_slots = {}
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

    def is_slot_available(self, day: int, time: int, teacher: Teacher, class_name: str, classroom: Classrooms) -> bool:

        # Check if the slot is the chosen recess slot for this day
        if self.chosen_recess_slots.get(day) == time:
            print(f"DEBUG: Slot {time} is the chosen recess slot for day {day}")
            return False
        # Check teacher availability
        try:
            teacher_availability = TeacherAvailability.objects.get(teacher=teacher, day=day)
            slot_field = f'slot_{time}_{time + 1}'
            if getattr(teacher_availability, slot_field) == AvailabilityStatus.NOT_AVAILABLE:
                return False
        except Teacher.DoesNotExist:
            print(f"!!DEBUG: No availability data for teacher {teacher}")
            # If no availability is defined, assume the teacher is available
            return False

        # Check classroom availability
        if not classroom.check_availability(time + 9):
            print(f"DEBUG: Classroom {classroom} not available")
            return False

        # Check if the slot is already booked
        existing_teacher_schedule = TeacherSchedule.objects.filter(
            teacher=teacher,
            day=day,
            hour=time + 9
        ).exists()

        if existing_teacher_schedule:
            print(f"DEBUG: Slot already booked")
            return False
            # Check if the slot is already booked for the class in `ClassSchedule`
        existing_class_schedule = ClassSchedule.objects.filter(
            class_object__name=class_name,
            day=day,
            hour=time + 9
        ).exists()

        if existing_class_schedule:
            print(f"DEBUG: Class {class_name} already has a scheduled session at this time")
            return False

        print(f"DEBUG: Slot is available")
        return True

    def generate_timetable(self):
        print("DEBUG: Starting timetable generation")
        self.prepare_data()

        # Schedule electives
        electives = Elective.objects.all()
        for elective in electives:
            print(f"DEBUG: Scheduling elective {elective.name}")

            # Get all classes and teachers associated with this elective
            classes = list(elective.class_pair.all())
            teachers = list(elective.teacher_pair.all())

            # Use the duration from the Elective model
            elective_duration = elective.duration
            lectures_to_schedule = elective.number_of_lectures

            lectures_scheduled = 0
            attempts = 0
            max_attempts = 100

            while lectures_scheduled < lectures_to_schedule and attempts < max_attempts:
                day = random.randint(0, self.num_days - 1)
                time = random.randint(0, self.time_slots - 1)

                # Check if all classes and teachers are available
                all_available = True
                available_classrooms = {}
                for class_obj in classes:
                    # Get available classrooms of the type specified by the elective
                    class_classrooms = Classrooms.objects.filter(classroom_type=elective.classroom_type)
                    class_available_classrooms = [
                        classroom for classroom in class_classrooms
                        if all(self.is_slot_available(day, time, teacher, class_obj.name, classroom)
                               for teacher in teachers)
                    ]
                    if not class_available_classrooms:
                        all_available = False
                        break
                    available_classrooms[class_obj] = class_available_classrooms

                if all_available:
                    # Book the slot for all classes and teachers, assigning a classroom for each class
                    for class_obj in classes:
                        classroom = random.choice(available_classrooms[class_obj])
                        # Book the slot for the class
                        book_class_slot(day, time, elective, elective_duration, classroom, class_obj.name)

                        for teacher in teachers:
                            # Book the slot for the teacher
                            book_teacher_slot(day, time, elective, elective_duration, classroom, teacher)

                    lectures_scheduled += 1

                attempts += 1

            if lectures_scheduled < lectures_to_schedule:
                print(f"WARNING: Could not schedule all lectures for elective {elective.name}. "
                      f"Scheduled {lectures_scheduled}/{lectures_to_schedule}")

        for class_name, teachers in self.classes.items():

            # Choose and book one recess slot for this class each day
            for day in range(self.num_days):
                recess_time = random.choice(self.potential_recess_slots)
                self.chosen_recess_slots[day] = recess_time

                # Use book_slot to book the recess for this class
                book_class_slot(day, recess_time, None, 1, None, class_name)
                print(f"DEBUG: Booked recess for class {class_name} on day {day} at time {recess_time + 9}")

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

                            if slots_available and not has_teacher_scheduled_class(day, teacher, class_name):
                                book_class_slot(day, time, class_subject, subject_duration, classroom, class_name)
                                book_teacher_slot(day, time, class_subject, subject_duration, classroom, teacher)

                            lectures_scheduled += 1
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
        class_schedules = ClassSchedule.objects.all()
        teacher_schedules = TeacherSchedule.objects.all()

        # Process class schedules
        for entry in class_schedules:
            day = entry.day
            time = entry.hour - 9  # Convert back to 0-based index

            class_name = entry.class_object.name if entry.class_object else 'Recess'

            # Handle cases where class_subject or classroom is None (like for recess slots)
            if entry.class_subject:
                subject = entry.class_subject.subject.name
            else:
                subject = 'Recess'

            classroom = entry.classroom.classroom_name if entry.classroom else 'N/A'

            schedule[day][time].append((class_name, subject, 'N/A', classroom))

        # Process teacher schedules
        for entry in teacher_schedules:
            day = entry.day
            time = entry.hour - 9  # Convert back to 0-based index

            class_name = entry.class_object.name
            teacher = entry.teacher.name

            # Update the schedule with teacher details
            for i, slot in enumerate(schedule[day][time]):
                if slot[0] == class_name:
                    schedule[day][time][i] = (slot[0], slot[1], teacher, slot[3])
                    break

        print(f"DEBUG: Schedule Prepares")
        print(f"Use print_timetable method to print the timetable")
        return schedule

    def print_timetable(self):
        print("DEBUG: Printing timetable")
        schedule = self.get_schedule()
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
        times = ['9-10', '10-11', '11-12', '12-1', '1-2', '2-3', '3-4', '4-5']

        # Dictionary to hold class and teacher schedules
        class_schedules = {}
        teacher_schedules = {}

        # Populate the schedules
        for day_index, day_schedule in enumerate(schedule):
            for time_index, slots in enumerate(day_schedule):
                for class_name, subject, teacher, classroom in slots:
                    # Update class schedule
                    if class_name not in class_schedules:
                        class_schedules[class_name] = [["Free" for _ in times] for _ in days]
                    class_schedules[class_name][day_index][time_index] = f"{subject} - {teacher} - {classroom}"

                    # Update teacher schedule
                    if teacher not in teacher_schedules:
                        teacher_schedules[teacher] = [["Free" for _ in times] for _ in days]
                    teacher_schedules[teacher][day_index][time_index] = f"{subject} - {class_name} - {classroom}"

        # Print timetable for each class
        for class_name, timetable in class_schedules.items():
            print(f"\nTimetable for {class_name}:")
            print("                ", end="")
            print(f"{'':10} | " + " | ".join(times))  # Print time slots header
            print("-" * (len(times) * 16))  # Print a separator line

            for day_index, day in enumerate(days):
                print(f"{day:8} | ", end="")  # Print day header
                print(" | ".join(timetable[day_index]))  # Print each day's timetable

        # Print timetable for each teacher
        for teacher_name, timetable in teacher_schedules.items():
            print(f"\nTimetable for {teacher_name}:")
            print("                ", end="")
            print(f"{'':10} | " + " | ".join(times))  # Print time slots header
            print("-" * (len(times) * 16))  # Print a separator line

            for day_index, day in enumerate(days):
                print(f"{day:8} | ", end="")  # Print day header
                print(" | ".join(timetable[day_index]))  # Print each day's timetable
