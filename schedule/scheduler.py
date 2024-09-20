import numpy as np
from typing import Dict, List, Tuple, Union
from timetable.schedule.models import Availability, AvailabilityStatus, ClassSubject
import random


class SchedulingService:
    def __init__(self, num_days: int = 6):  # Default to 6 if not provided
        self.num_days = num_days
        self.time_slots = 8  # 9 AM to 5 PM, 1-hour slots
        self.teachers = {}
        self.classes = {}
        self.schedule = []  # Initialize the schedule attribute

    def prepare_data(self, class_data: Dict[str, Dict[str, int]]):
        teachers = set()
        for class_teachers in class_data.values():
            teachers.update(class_teachers.keys())

        self.teachers = {teacher: np.zeros((self.num_days, self.time_slots), dtype=bool) for teacher in teachers}
        self.classes = {class_name: np.zeros((self.num_days, self.time_slots), dtype=bool) for class_name in
                        class_data.keys()}

    def is_slot_available(self, day: int, time: int, teacher: str, class_name: str) -> bool:
        # Mapping time integers to the correct slot fields in the Availability model
        slot_map = {
            0: 'slot_9_10',
            1: 'slot_10_11',
            2: 'slot_11_12',
            3: 'slot_12_1',
            4: 'slot_1_2',
            5: 'slot_2_3',
            6: 'slot_3_4',
            7: 'slot_4_5',
        }

        # Get the slot field for the provided time
        slot_field = slot_map.get(time)

        if not slot_field:
            raise ValueError("Invalid time slot. Please provide a time between 9 and 16.")

        # Check teacher availability
        try:
            teacher_availability = Availability.objects.get(teacher__name=teacher, day=day)
            teacher_slot_status = getattr(teacher_availability, slot_field)

            if teacher_slot_status == AvailabilityStatus.NOT_AVAILABLE:
                return False
        except Availability.DoesNotExist:
            # If no availability is defined, assume the teacher is not available
            return False

        # Check class availability (assumed to be stored in a similar way)
        try:
            class_availability = Availability.objects.get(class_name=class_name, day=day)
            class_slot_status = getattr(class_availability, slot_field)

            if class_slot_status == AvailabilityStatus.NOT_AVAILABLE:
                return False
        except Availability.DoesNotExist:
            # If no availability is defined for the class, assume it is not available
            return False

        # If both the teacher and class are available, return True
        return True

    def book_slot(self, day: int, time: int, teacher: str, class_name: str):
        self.teachers[teacher][day, time] = True
        self.classes[class_name][day, time] = True

    def has_teacher_scheduled_class(self, day: int, teacher_index: int, class_name: str) -> bool:
        # Check if the teacher has already been scheduled for this class on the given day
        for time in range(self.time_slots):
            scheduled_class_info = self.schedule[teacher_index][day][time]
            
            if isinstance(scheduled_class_info, tuple) and len(scheduled_class_info) >= 2:
                scheduled_class, _ = scheduled_class_info  # Unpack only the first two values
            else:
                scheduled_class = None  # Handle cases where the structure is unexpected

            if scheduled_class == class_name:
                return True
        return False

    def generate_schedule(self) -> List[List[List[Union[str, Tuple[str, str]]]]]:
        # Retrieve class data from the ClassSubject model
        class_data = {}
        class_subjects = ClassSubject.objects.select_related('class_name', 'teacher').all()

        for class_subject in class_subjects:
            class_name = class_subject.class_name.name
            teacher_name = class_subject.teacher.name
            sessions_per_week = class_subject.number_of_lectures

            if class_name not in class_data:
                class_data[class_name] = {}

            class_data[class_name][teacher_name] = sessions_per_week

        self.prepare_data(class_data)

        # Get unique teachers
        unique_teachers = list({teacher for teachers in class_data.values() for teacher in teachers.keys()})

        # Get unique classes
        unique_classes = list(class_data.keys())  # Extract unique class names

        # Initialize a 3D array for the schedule based on unique teachers and classes
        self.schedule = [[["Free" for _ in range(self.time_slots)] for _ in range(self.num_days)] for _ in
                         range(len(unique_teachers) + len(unique_classes))]

        # Schedule classes for each teacher
        for class_name, teacher_info in class_data.items():
            for teacher, sessions_per_week in teacher_info.items():
                sessions_scheduled = 0

                # Get the index of the teacher for the schedule array
                teacher_index = unique_teachers.index(teacher)

                while sessions_scheduled < sessions_per_week:
                    # Randomly shuffle the days and time slots
                    days = list(range(self.num_days))
                    times = list(range(self.time_slots))
                    random.shuffle(days)
                    random.shuffle(times)

                    scheduled = False
                    for day in days:
                        if self.has_teacher_scheduled_class(day, teacher_index, class_name):
                            continue  # Skip if the teacher already has a session for this class on the same day

                        for time in times:
                            if self.is_slot_available(day, time, teacher, class_name):
                                # Store class and teacher with a label
                                self.schedule[teacher_index][day][time] = (class_name, teacher)  # Store class and teacher
                                sessions_scheduled += 1
                                scheduled = True
                                print(f"Scheduled {class_name} with {teacher} on day {day}, time {time}")
                                # Break inner loops when required sessions are scheduled
                                if sessions_scheduled >= sessions_per_week:
                                    break
                        if sessions_scheduled >= sessions_per_week or scheduled:
                            break
                    if sessions_scheduled >= sessions_per_week:
                        break

        # Call print_all_timetables after generating the schedule
        print_all_timetables(self.schedule, unique_teachers, class_data)

        return self.schedule


def print_all_timetables(schedule, unique_teachers, class_data):
    # Print timetable for each teacher
    for teacher_index, teacher in enumerate(unique_teachers):
        print(f"Timetable for {teacher}:")
        for day in range(len(schedule[teacher_index])):
            print(f"  Day {day + 1}:")
            for time in range(len(schedule[teacher_index][day])):
                class_info = schedule[teacher_index][day][time]
                if class_info:
                    class_name, teacher_name = class_info
                    print(f"    Time Slot {time + 1}: {class_name} with {teacher_name}")
                else:
                    print(f"    Time Slot {time + 1}: Free")
        print()  # Add a blank line between teachers

    # Print timetable for each class
    for class_name in class_data.keys():
        print(f"Timetable for {class_name}:")
        for day in range(len(schedule[0])):  # Iterate through days
            print(f"  Day {day + 1}:")
            for time in range(len(schedule)):  # Iterate through teachers
                class_found = False
                for teacher_index, teacher in enumerate(unique_teachers):
                    class_info = schedule[teacher_index][day][time]
                    if class_info and class_info[0] == class_name:
                        print(f"    Time Slot {time + 1}: {class_name} with {teacher}")
                        class_found = True
                        break
                if not class_found:
                    print(f"    Time Slot {time + 1}: Free")
        print()  # Add a blank line after each class timetable
