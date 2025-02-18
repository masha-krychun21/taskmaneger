# Generated by Django 5.1.6 on 2025-02-14 13:05

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("custom_auth", "0010_alter_customuser_email_alter_customuser_username"),
    ]

    operations = [
        migrations.AlterField(
            model_name="team",
            name="users",
            field=models.ManyToManyField(blank=True, through="custom_auth.UserTeam", to=settings.AUTH_USER_MODEL),
        ),
    ]
