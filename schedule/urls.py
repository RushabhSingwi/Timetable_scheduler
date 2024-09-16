from django.urls import path
from .views import GenerateScheduleView, TeacherCreateView

urlpatterns = [
    path('generate-schedule/', GenerateScheduleView.as_view(), name='generate-schedule'),
    path('teachers/', TeacherCreateView.as_view(), name='teacher-create'),
]
