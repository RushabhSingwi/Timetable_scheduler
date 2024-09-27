from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view

from .scheduler import SchedulingService
from .serializers import TeacherSerializer, ClassSubjectSerializer, \
    SubjectSerializer, ClassSerializer, BookSlotSerializer


# def frontend(request):
#     return render(request, '../static/frontend/index.html')


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

        # Combine days and time slots for easier access in the template
        timetable = []
        for day_index, day_schedule in enumerate(schedule):
            day_data = []
            for time_index, time_slot in enumerate(day_schedule):
                day_data.append({
                    'time': times[time_index],
                    'classes': time_slot  # This is the list of classes in the current slot
                })
            timetable.append({
                'day': days[day_index],
                'slots': day_data
            })

        context = {
            'timetable': timetable
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


@api_view(['GET'])
def example_view(request):
    data = {"message": "Hello from Django!"}
    return Response(data)
