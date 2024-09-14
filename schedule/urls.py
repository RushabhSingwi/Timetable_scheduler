from django.urls import path
from .views import GenerateScheduleView

urlpatterns = [
    path('generate-schedule/', GenerateScheduleView.as_view(), name='generate-schedule'),
]