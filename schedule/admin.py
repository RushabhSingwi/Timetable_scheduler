from django.contrib import admin

from .models import Teacher, Subject, ClassSubject, Class, Classrooms


# Register your models here.
@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')  # Customize the columns you want to display in the admin list view
    search_fields = ('name',)


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'duration')  # Show the 'id', 'name' and 'duration' columns in the list view
    search_fields = ('name',)  # Enable searching by the 'name' field


@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')  # Show 'id' and 'name' in the admin list view
    search_fields = ('name',)  # Enable searching by the 'name' field


@admin.register(ClassSubject)
class ClassSubjectAdmin(admin.ModelAdmin):
    list_display = ('id', 'class_name', 'subject', 'teacher', 'number_of_lectures')
    search_fields = (
        'class_name__name', 'subject__name', 'teacher__name')  # Enable searching by class, subject, and teacher names
    list_filter = ('class_name', 'subject', 'teacher')  # Filter by class, subject, and teacher


@admin.register(Classrooms)
class ClassroomsAdmin(admin.ModelAdmin):
    list_display = ['classroom_type', 'number_of_classroom']
