from datetime import timedelta

from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import ClassSubject
from .scheduler import SchedulingService
from .serializers import TeacherSerializer, ClassSubjectSerializer, \
    SubjectSerializer, ClassSerializer, BookSlotSerializer


class TeacherCreateView(APIView):
    def post(self, request):
        serializer = TeacherSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Subject Create View
class SubjectCreateView(APIView):
    def post(self, request):
        serializer = SubjectSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Class Create View
class ClassCreateView(APIView):
    def post(self, request):
        serializer = ClassSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ClassSubjectCreateView(APIView):
    def post(self, request):
        serializer = ClassSubjectSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GenerateScheduleView(APIView):
    def get(self, request):
        num_days = int(request.GET.get('num_days', 6))

        # Your existing code to get the schedule
        scheduling_service = SchedulingService(num_days)
        schedule = scheduling_service.generate_timetable()

        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
        times = ['9-10', '10-11', '11-12', '12-1', '1-2', '2-3', '3-4', '4-5']

        class_schedules = {}

        for day_index, day_schedule in enumerate(schedule):
            for time_index, slots in enumerate(day_schedule):
                for class_name, subject, teacher in slots:
                    if class_name not in class_schedules:
                        class_schedules[class_name] = [["Free" for _ in times] for _ in days]
                    class_schedules[class_name][day_index][time_index] = f"{subject} - {teacher}"

        # Prepare days with indices
        indexed_days = list(enumerate(days))

        context = {
            'class_schedules': class_schedules,
            'indexed_days': indexed_days,
            'times': times,
        }

        return render(request, 'timetable.html', context)


class BookSlotView(APIView):
    def post(self, request):
        serializer = BookSlotSerializer(data=request.data)

        # Validate incoming data
        if serializer.is_valid():
            # Create the schedule slot using validated data
            schedule = serializer.save()
            return Response({"message": "Slot booked successfully"}, status=status.HTTP_201_CREATED)

        # Return errors if the data is invalid
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
