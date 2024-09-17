from django.urls import path
from .views import GenerateScheduleView, TeacherCreateView, ClassSubjectCreateView

urlpatterns = [
    path('generate-schedule/', GenerateScheduleView.as_view(), name='generate-schedule'),
    path('teachers/', TeacherCreateView.as_view(), name='teacher-create'),
    path('add-class-subject/', ClassSubjectCreateView.as_view(), name='add-class-subject'),
]
