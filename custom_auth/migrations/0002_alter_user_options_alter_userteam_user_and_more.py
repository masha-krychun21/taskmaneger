# Generated by Django 5.1.5 on 2025-02-06 13:28

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("custom_auth", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="user",
            options={"verbose_name": "user", "verbose_name_plural": "users"},
        ),
        migrations.AlterField(
            model_name="userteam",
            name="user",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="custom_auth.customuser"),
        ),
        migrations.AlterModelTable(
            name="user",
            table=None,
        ),
    ]
