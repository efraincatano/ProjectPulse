# Generated by Django 5.0.4 on 2024-10-03 20:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0002_project_iduser_admin_notes'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='project',
            name='iduser_admin',
        ),
    ]