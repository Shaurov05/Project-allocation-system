# Generated by Django 3.1.3 on 2021-02-22 15:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0002_auto_20210222_2157'),
    ]

    operations = [
        migrations.RenameField(
            model_name='student',
            old_name='assigned_project',
            new_name='assigned_project_id',
        ),
    ]
