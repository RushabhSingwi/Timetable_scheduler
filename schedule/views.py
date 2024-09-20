from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Teacher, Class, Schedule
from .serializers import ScheduleSerializer, TeacherSerializer, ClassSubjectSerializer, \
    SubjectSerializer, ClassSerializer
from .scheduler import SchedulingService

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
        # Get num_days from query parameters, default to 6 if not provided
        num_days = int(request.GET.get('num_days', 6))  # Convert to int, default to 6

        # Instantiate the scheduling service
        scheduling_service = SchedulingService(num_days)

        # Call the generate_schedule method
        schedule = scheduling_service.generate_schedule()

        # Return the schedule as a JSON response
        return JsonResponse({"schedule": schedule})
