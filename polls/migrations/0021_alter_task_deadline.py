# Generated by Django 5.1.5 on 2025-02-19 14:37

import datetime

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("polls", "0020_task_reminder_1h_task_reminder_24h_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="task",
            name="deadline",
            field=models.DateTimeField(default=datetime.datetime.now),
        ),
    ]
