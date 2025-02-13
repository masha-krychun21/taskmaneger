# Generated by Django 5.1.5 on 2025-02-06 08:43

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("polls", "0005_alter_task_status_delete_taskstatus"),
    ]

    operations = [
        migrations.AlterField(
            model_name="comment",
            name="task",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="comments_set",
                to="polls.task",
            ),
        ),
        migrations.CreateModel(
            name="TaskComment",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("text", models.TextField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "task",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="task_comments_set",
                        to="polls.task",
                    ),
                ),
            ],
        ),
    ]
