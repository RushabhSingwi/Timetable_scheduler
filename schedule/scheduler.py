import numpy as np
from typing import Dict, List, Tuple
from .models import Teacher, Class, Schedule


class SchedulingService:
    def __init__(self, num_days: int):
        self.num_days = num_days
        self.time_slots = 9  # 9 AM to 5 PM, 1-hour slots
        self.teachers = {}
        self.classes = {}

    def prepare_data(self, class_data: Dict[str, Dict[str, int]]):
        teachers = set()
        for class_teachers in class_data.values():
            teachers.update(class_teachers.keys())

        self.teachers = {teacher: np.zeros((self.num_days, self.time_slots), dtype=bool) for teacher in teachers}
        self.classes = {class_name: np.zeros((self.num_days, self.time_slots), dtype=bool) for class_name in
                        class_data.keys()}

    def is_slot_available(self, day: int, time: int, teacher: str, class_name: str) -> bool:
        return (not self.teachers[teacher][day, time] and
                not self.classes[class_name][day, time])

    def book_slot(self, day: int, time: int, teacher: str, class_name: str):
        self.teachers[teacher][day, time] = True
        self.classes[class_name][day, time] = True

    def generate_schedule(self, class_data: Dict[str, Dict[str, int]]) -> List[Tuple[int, int, str, str]]:
        self.prepare_data(class_data)
        schedule = []
        for class_name, teacher_info in class_data.items():
            for teacher, sessions_per_week in teacher_info.items():
                sessions_scheduled = 0
                while sessions_scheduled < sessions_per_week:
                    scheduled = False
                    for day in range(self.num_days):
                        if scheduled:
                            break
                        for time in range(self.time_slots):
                            if self.is_slot_available(day, time, teacher, class_name):
                                self.book_slot(day, time, teacher, class_name)
                                schedule.append((day, time, teacher, class_name))
                                scheduled = True
                                sessions_scheduled += 1
                                break
                    if not scheduled:
                        print(f"Unable to schedule all sessions for {class_name} with {teacher}")
                        break
        return schedule