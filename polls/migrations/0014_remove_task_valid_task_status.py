# Generated by Django 5.1.5 on 2025-02-12 12:49

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("polls", "0013_task_team_task_valid_task_status"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="task",
            name="valid_task_status",
        ),
    ]
