from django.db import models

class Teacher(models.Model):
    name = models.CharField(max_length=100)

class Class(models.Model):
    name = models.CharField(max_length=100)

class Schedule(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    class_name = models.ForeignKey(Class, on_delete=models.CASCADE)
    day = models.IntegerField()
    time = models.IntegerField()