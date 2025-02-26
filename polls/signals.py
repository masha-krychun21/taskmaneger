# from datetime import datetime, timedelta
from celery import shared_task
from django.apps import AppConfig
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone

from .models import Notification, NotificationSettings, Task, TaskHistory  # TaskReminder

# naive_deadline = datetime(2025, 2, 21, 12, 30, 0)
# aware_deadline = timezone.make_aware(naive_deadline)
# current_time = timezone.now()


class PollsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "polls"

    def ready(self):
        pass


@receiver(pre_save, sender=Task)
def track_task_status_change(sender, instance, **kwargs):
    if instance.pk:
        previous_task = Task.objects.get(pk=instance.pk)
        if previous_task.status != instance.status:
            instance._previous_status = previous_task.status


@receiver(post_save, sender=Task)
def create_task_status_notification(sender, instance, created, **kwargs):
    if created:
        message = f"Нове завдання: {instance.title}"
    elif hasattr(instance, "_previous_status") and instance._previous_status != instance.status:
        message = f"Статус задачі '{instance.title}' змінено на '{instance.get_status_display()}'"
    else:
        return

    settings = NotificationSettings.objects.filter(user=instance.assigned_to).first()
    if settings and settings.status_change:
        Notification.objects.create(user=instance.assigned_to, message=message)


@receiver(post_save, sender=Task)
def log_task_history(sender, instance, created, **kwargs):
    if not created and hasattr(instance, "_previous_status") and instance._previous_status != instance.status:
        TaskHistory.objects.create(
            task=instance,
            user=instance.assigned_to,
            action=f"Статус змінено на {instance.get_status_display()}",
            previous_value=instance._previous_status,
        )


# @receiver(post_save, sender=Task)
# def create_deadline_reminders(sender, instance, **kwargs):
#     if instance.deadline:
#         TaskReminder.objects.filter(task=instance).delete()

#         reminders = [
#             (instance.deadline - timedelta(hours=24), "24 години"),
#             (instance.deadline - timedelta(hours=1), "1 година"),
#         ]

#         for remind_at, _ in reminders:
#             if timezone.is_naive(remind_at):
#                 remind_at = timezone.make_aware(remind_at)
#             if remind_at > timezone.now():
#                 TaskReminder.objects.create(task=instance, user=instance.assigned_to, remind_at=remind_at)


# def send_task_reminders():
#     reminders = TaskReminder.objects.filter(remind_at__lte=timezone.now(), sent=False)

#     for reminder in reminders:
#         if timezone.is_naive(reminder.remind_at):
#             reminder.remind_at = timezone.make_aware(reminder.remind_at)

#         Notification.objects.create(
#             user=reminder.user,
#             message=f"Нагадування: Завдання '{reminder.task.title}' має дедлайн {reminder.task.deadline}"
#         )
#         reminder.sent = True
#         reminder.save()


@shared_task
def send_deadline_notifications():
    tasks = Task.objects.filter(deadline__lte=timezone.now())
    for task in tasks:
        user = task.assigned_to
        Notification.objects.create(user=user, message=f"Завдання {task.title} наближається до дедлайну.")
