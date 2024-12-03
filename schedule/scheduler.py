import random
from datetime import timedelta
from typing import List, Tuple, Optional, Dict, Union

from django.db import transaction

from .models import (ClassSubject, Teacher, Classrooms,
                     Class, ClassSchedule, TeacherSchedule)


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
            classroom.book_classroom(day, (time + slot_offset))


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


class MultiLabScheduler:
    def __init__(self, num_days: int = 6):
        self.num_days = num_days
        self.time_slots = 8
        self.lab_duration = 2  # Lab sessions are 2 hours long

    def schedule_lab_sessions(self, class_obj: Class, lab_subjects: List[ClassSubject], sessions_per_week: int) -> bool:
        """
        Schedule multiple lab sessions for a class, ensuring at most one per day.

        :param class_obj: The class to schedule lab sessions for
        :param lab_subjects: List of lab subjects to be scheduled
        :param sessions_per_week: Number of lab sessions to schedule per week
        :return: True if all sessions were successfully scheduled, False otherwise
        """
        if not lab_subjects:
            print(f"ERROR: No lab subjects provided for {class_obj.name}")
            return False

        scheduled_sessions = 0
        available_slots = self.get_available_slots(class_obj)

        while scheduled_sessions < sessions_per_week and available_slots:
            day, time = random.choice(list(available_slots.keys()))
            lab_subject = random.choice(lab_subjects)

            if self.schedule_single_lab_session(class_obj, lab_subject, day, time):
                scheduled_sessions += 1
                # Remove all slots for this day to ensure only one lab per day
                available_slots = {k: v for k, v in available_slots.items() if k[0] != day}
            else:
                # Remove this slot if scheduling failed
                del available_slots[(day, time)]

        if scheduled_sessions < sessions_per_week:
            print(
                f"WARNING: Could only schedule {scheduled_sessions}/{sessions_per_week} "
                f"lab sessions for {class_obj.name}")
            return False

        print(f"DEBUG: Successfully scheduled {scheduled_sessions} lab sessions for {class_obj.name}")
        return True

    def get_available_slots(self, class_obj: Class) -> Dict[Tuple[int, int], List[Classrooms]]:
        available_slots = {}
        for day in range(self.num_days):
            for time in range(self.time_slots - self.lab_duration + 1):  # Ensure we don't overflow time slots
                classrooms = self.get_available_classrooms(class_obj, day, time)
                if classrooms:
                    available_slots[(day, time)] = classrooms
        return available_slots

    def get_available_classrooms(self, class_obj: Class, day: int, time: int) -> List[Classrooms]:
        lab_classroom_types = set(subject.subject.classroom_type for subject in
                                  class_obj.classsubject_set.filter(subject__classroom_type__name='Laboratory'))
        available_classrooms = []

        for classroom_type in lab_classroom_types:
            classrooms = Classrooms.objects.filter(classroom_type=classroom_type)
            for classroom in classrooms:
                if self.is_slot_available(day, time, classroom, self.lab_duration):
                    available_classrooms.append(classroom)

        return available_classrooms

    def is_slot_available(self, day: int, time: int, classroom: Classrooms, duration: int) -> bool:
        for hour in range(time, time + duration):
            if ClassSchedule.objects.filter(day=day, hour=hour + 9, classroom=classroom).exists():
                return False
        return True

    def schedule_single_lab_session(self, class_obj: Class, lab_subject: ClassSubject, day: int, time: int) -> bool:
        classroom = self.get_available_classrooms(class_obj, day, time)[0]  # Get the first available classroom
        teacher = lab_subject.teacher

        if not self.is_teacher_available(teacher, day, time):
            print(f"DEBUG: Teacher {teacher.name} not available for lab on day {day}, time {time}")
            return False

        with transaction.atomic():
            self.book_lab_slot(day, time, lab_subject, classroom, class_obj)
            self.book_teacher_slot(day, time, teacher, classroom, class_obj)

        print(f"DEBUG: Scheduled lab session for {class_obj.name} on day {day}, time {time}")
        return True

    def is_teacher_available(self, teacher: Teacher, day: int, time: int) -> bool:
        for hour in range(time, time + self.lab_duration):
            if TeacherSchedule.objects.filter(teacher=teacher, day=day, hour=hour + 9).exists():
                return False
        return True


def delete_all_schedules():
    """Deletes all entries in the Schedule model."""
    ClassSchedule.objects.all().delete()
    TeacherSchedule.objects.all().delete()
    print("All schedule entries have been deleted.")


def book_class_slot(day: int, time: int, class_subject: Optional[ClassSubject], duration: int,
              classroom: Optional[Classrooms], class_name: str):
    print(f"DEBUG: Booking slot for day {day}, time {time}, class subject {class_subject}")

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


def book_lab_slot(self, day: int, time: int, lab_subject: ClassSubject, classroom: Classrooms, class_obj: Class):
    for hour in range(self.lab_duration):
        ClassSchedule.objects.create(
            class_subject=lab_subject,
            day=day,
            hour=time + hour + 9,
            duration=timedelta(hours=1),
            classroom=classroom,
            class_object=class_obj
        )


def has_teacher_scheduled_class(day: int, teacher: str, class_name: str) -> bool:
    print(f"DEBUG: Checking if teacher {teacher} is already scheduled for class {class_name} on day {day}")
    exists = Schedule.objects.filter(
        class_subject__teacher__name=teacher,
        class_subject__class_name__name=class_name,
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
        print("DEBUG: TimetableGenerator initialized")

    def prepare_data(self):
        print("DEBUG: Preparing data")
        # Fetch all ClassSubject entries
        class_subjects = ClassSubject.objects.all()

        # Prepare data structures
        for cs in class_subjects:
            if cs.class_name.name not in self.classes:
                self.classes[cs.class_name.name] = {}
            self.classes[cs.class_name.name][cs.teacher.name] = cs.number_of_lectures

            if cs.teacher.name not in self.teachers:
                self.teachers[cs.teacher.name] = {}

        print(f"DEBUG: Prepared data - Classes: {self.classes}, Teachers: {self.teachers}")

    def is_slot_available(self, day: int, time: int, teacher: Union[Teacher, str],
                          class_name: str, classroom: Classrooms) -> bool:

        if isinstance(teacher, str):
            try:
                teacher = Teacher.objects.get(name=teacher)
            except Teacher.DoesNotExist:
                print(f"!!DEBUG: No teacher found with name {teacher}")
                return False

        # Check if the slot is the chosen recess slot for this day
        if self.chosen_recess_slots.get(day) == time+9:
            print(f"DEBUG: Slot {time} is the chosen recess slot for day {day}")
            return False

        # Check if teacher is available
        if not teacher.is_available(day, time+9):
            print(f"DEBUG: Teacher {teacher.name} is not available.")
            return False

        # Check classroom availability
        if not classroom.is_classroom_available(day, time):
            print(f"DEBUG: Classroom {classroom} not available")
            return False

        # Check if slot is booked for the teacher or class
        if TeacherSchedule.objects.filter(teacher=teacher, day=day, hour=time + 9).exists():
            print(f"DEBUG: Slot already booked for teacher {teacher.name}.")
            return False

        if ClassSchedule.objects.filter(class_object__name=class_name, day=day, hour=time + 9).exists():
            print(f"DEBUG: Class {class_name} already has a session at this time.")
            return False

        print(f"DEBUG: Slot is available")
        return True

    def generate_timetable(self):
        print("DEBUG: Starting timetable generation")
        delete_all_schedules()
        self.prepare_data()

        for class_name in self.classes:
            # Choose and book one recess slot for this class each day
            for day in range(self.num_days):
                recess_time = random.choice(self.potential_recess_slots)
                self.chosen_recess_slots[day] = recess_time
                # Use book_slot to book the recess for this class
                book_class_slot(day, recess_time, None, 1, None, class_name)
                print(f"DEBUG: Booked recess for class {class_name} on day {day} at time {recess_time + 9}")
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

            schedule[day][time].append((class_name, subject, teacher, classroom))

        print(f"DEBUG: Schedule Prepares")
        print(f"Use print_timetable method to print the timetable")
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

        # Populate the class schedules
        for day_index, day_schedule in enumerate(schedule):
            for time_index, slots in enumerate(day_schedule):
                for class_name, subject, teacher, classroom in slots:
                    if class_name not in class_schedules:
                        class_schedules[class_name] = [["Free" for _ in times] for _ in days]
                    class_schedules[class_name][day_index][time_index] = f"{subject} - {teacher} - {classroom}"

                    # Update teacher schedule
                    if teacher not in teacher_schedules:
                        teacher_schedules[teacher] = [["Free" for _ in times] for _ in days]
                    teacher_schedules[teacher][day_index][time_index] = f"{class_name} - {subject} - {classroom}"

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
