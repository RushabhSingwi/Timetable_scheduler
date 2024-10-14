from django.contrib import admin

from .models import Teacher, Subject, ClassSubject, Class, Classrooms, Elective, TeacherSchedule, ClassSchedule


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
    list_display = ['classroom_type']


@admin.register(Elective)
class ElectiveAdmin(admin.ModelAdmin):
    list_display = ('name', 'subject_code')  # Specify which fields to display in the list view
    search_fields = ('name', 'subject_code')  # Allow searching by these fields


@admin.register(TeacherSchedule)
class TeacherScheduleAdmin(admin.ModelAdmin):
    list_display = ['teacher', 'day', 'hour', 'classroom', 'class_object']
    list_filter = ['teacher', 'day', 'hour', 'classroom', 'class_object']
    search_fields = ['teacher__name', 'classroom__classroom_name', 'class_object__name']

@admin.register(ClassSchedule)
class ClassScheduleAdmin(admin.ModelAdmin):
    list_display = ['id', 'day', 'hour', 'get_subject', 'get_teacher', 'classroom', 'class_object']
    list_filter = ['day', 'hour', 'classroom', 'class_object']
    search_fields = ['class_subject__subject__name', 'class_subject__teacher__name', 'classroom__classroom_name', 'class_object__name']

    def get_subject(self, obj):
        return obj.class_subject.subject.name if obj.class_subject else '-'
    get_subject.short_description = 'Subject'

    def get_teacher(self, obj):
        return obj.class_subject.teacher.name if obj.class_subject else '-'
    get_teacher.short_description = 'Teacher'

