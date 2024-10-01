# Generated by Django 4.2.15 on 2024-10-01 11:33

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Class',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Classrooms',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('classroom_name', models.CharField(max_length=10)),
                ('slot_9_10', models.CharField(choices=[('A', 'Available'), ('N', 'Not Available')], default='A', max_length=1)),
                ('slot_10_11', models.CharField(choices=[('A', 'Available'), ('N', 'Not Available')], default='A', max_length=1)),
                ('slot_11_12', models.CharField(choices=[('A', 'Available'), ('N', 'Not Available')], default='A', max_length=1)),
                ('slot_12_1', models.CharField(choices=[('A', 'Available'), ('N', 'Not Available')], default='A', max_length=1)),
                ('slot_1_2', models.CharField(choices=[('A', 'Available'), ('N', 'Not Available')], default='A', max_length=1)),
                ('slot_2_3', models.CharField(choices=[('A', 'Available'), ('N', 'Not Available')], default='A', max_length=1)),
                ('slot_3_4', models.CharField(choices=[('A', 'Available'), ('N', 'Not Available')], default='A', max_length=1)),
                ('slot_4_5', models.CharField(choices=[('A', 'Available'), ('N', 'Not Available')], default='A', max_length=1)),
            ],
        ),
        migrations.CreateModel(
            name='ClassroomType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='ClassSubject',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number_of_lectures', models.IntegerField()),
                ('class_name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='schedule.class')),
            ],
        ),
        migrations.CreateModel(
            name='Teacher',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Subject',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('duration', models.IntegerField(default=1)),
                ('subject_code', models.CharField(max_length=20)),
                ('classroom', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='schedule.classrooms')),
            ],
        ),
        migrations.CreateModel(
            name='Schedule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day', models.IntegerField()),
                ('hour', models.IntegerField()),
                ('duration', models.DurationField(default=datetime.timedelta(seconds=3600))),
                ('class_subject', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='schedule.classsubject')),
            ],
        ),
        migrations.AddField(
            model_name='classsubject',
            name='subject',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='schedule.subject'),
        ),
        migrations.AddField(
            model_name='classsubject',
            name='teacher',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='schedule.teacher'),
        ),
        migrations.AddField(
            model_name='classrooms',
            name='classroom_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='schedule.classroomtype'),
        ),
        migrations.CreateModel(
            name='Availability',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day', models.IntegerField()),
                ('slot_9_10', models.CharField(choices=[('A', 'Available'), ('N', 'Not Available')], default='A', max_length=1)),
                ('slot_10_11', models.CharField(choices=[('A', 'Available'), ('N', 'Not Available')], default='A', max_length=1)),
                ('slot_11_12', models.CharField(choices=[('A', 'Available'), ('N', 'Not Available')], default='A', max_length=1)),
                ('slot_12_1', models.CharField(choices=[('A', 'Available'), ('N', 'Not Available')], default='A', max_length=1)),
                ('slot_1_2', models.CharField(choices=[('A', 'Available'), ('N', 'Not Available')], default='A', max_length=1)),
                ('slot_2_3', models.CharField(choices=[('A', 'Available'), ('N', 'Not Available')], default='A', max_length=1)),
                ('slot_3_4', models.CharField(choices=[('A', 'Available'), ('N', 'Not Available')], default='A', max_length=1)),
                ('slot_4_5', models.CharField(choices=[('A', 'Available'), ('N', 'Not Available')], default='A', max_length=1)),
                ('teacher', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='schedule.teacher')),
            ],
        ),
    ]
