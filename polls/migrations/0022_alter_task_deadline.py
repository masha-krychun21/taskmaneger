# Generated by Django 5.1.5 on 2025-02-21 10:27

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("polls", "0021_alter_task_deadline"),
    ]

    operations = [
        migrations.AlterField(
            model_name="task",
            name="deadline",
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
