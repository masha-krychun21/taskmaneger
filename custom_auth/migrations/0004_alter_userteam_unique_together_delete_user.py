# Generated by Django 5.1.5 on 2025-02-07 09:02

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("custom_auth", "0003_alter_role_name"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="userteam",
            unique_together={("user", "team")},
        ),
        migrations.DeleteModel(
            name="User",
        ),
    ]
