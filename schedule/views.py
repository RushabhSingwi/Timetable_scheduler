from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Teacher, Class, Schedule
from .serializers import ScheduleSerializer, ScheduleInputSerializer
from .scheduler import SchedulingService

class GenerateScheduleView(APIView):
    def post(self, request):
        serializer = ScheduleInputSerializer(data=request.data)
        if serializer.is_valid():
            num_days = serializer.validated_data['num_days']
            class_data = serializer.validated_data['classes']

            scheduling_service = SchedulingService(num_days)
            schedule = scheduling_service.generate_schedule(class_data)

            # Save the generated schedule to the database
            saved_schedules = []
            for day, time, teacher_name, class_name in schedule:
                teacher, _ = Teacher.objects.get_or_create(name=teacher_name)
                class_, _ = Class.objects.get_or_create(name=class_name)
                saved_schedule = Schedule.objects.create(
                    teacher=teacher,
                    class_name=class_,
                    day=day,
                    time=time
                )
                saved_schedules.append(saved_schedule)

            # Serialize and return the saved schedules
            return Response(ScheduleSerializer(saved_schedules, many=True).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
