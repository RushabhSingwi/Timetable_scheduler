from django.urls import path
from .views import (GenerateScheduleView, TeacherCreateView, ClassSubjectCreateView, SubjectCreateView, ClassCreateView,
                    BookSlotView)

urlpatterns = [
    # path('', frontend, name='frontend'),
    path('generate-schedule/', GenerateScheduleView.as_view(), name='generate-schedule'),
    path('teachers/', TeacherCreateView.as_view(), name='teacher-create'),
    path('add-class-subject/', ClassSubjectCreateView.as_view(), name='add-class-subject'),
    path('add-subject/', SubjectCreateView.as_view(), name='add-subject'),
    path('add-class/', ClassCreateView.as_view(), name='add-class'),
    path('book-slot/', BookSlotView.as_view(), name='book-slot')
]
