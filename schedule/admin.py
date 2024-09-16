from django.contrib import admin

from .models import Teacher


# Register your models here.
@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')  # Customize the columns you want to display in the admin list view
    search_fields = ('name',)
