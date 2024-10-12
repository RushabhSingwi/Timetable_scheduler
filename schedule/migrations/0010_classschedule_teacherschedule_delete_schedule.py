# Generated by Django 4.2.15 on 2024-10-11 17:48

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0009_elective_classroom_type_elective_duration_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ClassSchedule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day', models.IntegerField()),
                ('hour', models.IntegerField()),
                ('duration', models.DurationField(default=datetime.timedelta(seconds=3600))),
                ('class_object', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='schedule.class')),
                ('class_subject', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='schedule.classsubject')),
                ('classroom', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='schedule.classrooms')),
            ],
        ),
        migrations.CreateModel(
            name='TeacherSchedule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day', models.IntegerField()),
                ('hour', models.IntegerField()),
                ('duration', models.DurationField(default=datetime.timedelta(seconds=3600))),
                ('class_object', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='schedule.class')),
                ('classroom', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='schedule.classrooms')),
                ('teacher', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='schedule.teacher')),
            ],
        ),
        migrations.DeleteModel(
            name='Schedule',
        ),
    ]
