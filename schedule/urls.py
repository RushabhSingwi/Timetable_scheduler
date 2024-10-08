from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (GenerateScheduleView, TeacherCreateView, ClassSubjectCreateView, SubjectCreateView, ClassCreateView,
                    BookSlotView, ClassroomTypeCreateView, ClassroomsCreateView, ClassroomBookingView, ElectiveViewSet)

router = DefaultRouter()
router.register(r'electives', ElectiveViewSet, basename='elective')


urlpatterns = [
    # path('', frontend, name='frontend'),
    path('generate-schedule/', GenerateScheduleView.as_view(), name='generate-schedule'),
    path('teachers/', TeacherCreateView.as_view(), name='teacher-create'),
    path('add-class-subject/', ClassSubjectCreateView.as_view(), name='add-class-subject'),
    path('add-subject/', SubjectCreateView.as_view(), name='add-subject'),
    path('add-class/', ClassCreateView.as_view(), name='add-class'),
    path('book-slot/', BookSlotView.as_view(), name='book-slot'),
    path('classroom-types/', ClassroomTypeCreateView.as_view(), name='classroom-type-create'),
    path('classrooms/', ClassroomsCreateView.as_view(), name='classroom-create'),
    path('book-classroom/', ClassroomBookingView.as_view(), name='book-classroom'),

    path('electives', include(router.urls)),
]
