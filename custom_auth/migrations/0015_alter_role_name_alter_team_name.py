# Generated by Django 5.1.6 on 2025-02-14 13:29

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("custom_auth", "0014_alter_customuser_email"),
    ]

    operations = [
        migrations.AlterField(
            model_name="role",
            name="name",
            field=models.CharField(max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name="team",
            name="name",
            field=models.CharField(max_length=255),
        ),
    ]
