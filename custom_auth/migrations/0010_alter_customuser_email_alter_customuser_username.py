# Generated by Django 5.1.5 on 2025-02-14 12:12

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("custom_auth", "0009_userteam_role"),
    ]

    operations = [
        migrations.AlterField(
            model_name="customuser",
            name="email",
            field=models.EmailField(max_length=254),
        ),
        migrations.AlterField(
            model_name="customuser",
            name="username",
            field=models.CharField(max_length=100, unique=True),
        ),
    ]
