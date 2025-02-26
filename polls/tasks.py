from datetime import timedelta

from django.utils import timezone

from mysite.celery import app

from .models import Notification, Task


@app.task
def deadline_notification():
    now = timezone.now()
    one_hour = timedelta(hours=1)
    one_day = timedelta(days=1)
    time_margin = timedelta(seconds=30)

    tasks = Task.objects.filter(deadline__gte=now, deadline__lte=now + one_day)

    for task in tasks:
        if timezone.is_naive(task.deadline):
            task.deadline = timezone.make_aware(task.deadline)
            task.save(update_fields=["deadline"])

        time_left = task.deadline - now

        if abs(time_left - one_hour) <= time_margin and not task.reminder_1h:
            message = f"Нагадування: Завдання '{task.title}' має дедлайн через 1 годину ({task.deadline})"
            Notification.objects.create(user=task.assigned_to, message=message)
            task.reminder_1h = True
            task.save(update_fields=["reminder_1h"])

        elif abs(time_left - one_day) <= time_margin and not task.reminder_24h:
            message = f"Нагадування: Завдання '{task.title}' має дедлайн через 24 години ({task.deadline})"
            Notification.objects.create(user=task.assigned_to, message=message)
            task.reminder_24h = True
            task.save(update_fields=["reminder_24h"])
