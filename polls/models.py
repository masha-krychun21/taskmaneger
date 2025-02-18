from django.conf import settings
from django.db import models

from custom_auth.models import CustomUser


class TaskStatus(models.TextChoices):
    NEW = "new", "Нова"
    IN_PROGRESS = "in_progress", "В процесі"
    WAITING_FOR_REVIEW = "waiting_for_review", "Очікує перевірки"
    REWORK = "rework", "Повернуто на доробку"
    COMPLETED = "completed", "Завершена"


class Task(models.Model):
    title: str = models.CharField(max_length=100)
    description: str = models.TextField()
    assigned_to: models.ForeignKey = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="tasks"
    )
    status: str = models.CharField(
        max_length=20,
        choices=TaskStatus.choices,
        default=TaskStatus.NEW,
        verbose_name="Статус",
    )
    team = models.ForeignKey(
        "custom_auth.Team",
        on_delete=models.CASCADE,
        related_name="tasks",
        null=True,
        blank=True,
    )
    deadline: models.DateTimeField = models.DateTimeField(null=True, blank=True)
    time_spent = models.DurationField(null=True, blank=True)
    created_at: models.DateTimeField = models.DateTimeField(auto_now_add=True)
    updated_at: models.DateTimeField = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.title


class Comment(models.Model):
    task: models.ForeignKey = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="comments")
    user: str = models.CharField(max_length=255)
    text: str = models.TextField()
    created_at: models.DateTimeField = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Comment by {self.user} on {self.task}"


class Notification(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    message = models.TextField()
    status = models.CharField(max_length=20, default="unread")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Notification: {self.message}"

    def mark_as_read(self):
        self.status = "read"
        self.save()

    def mark_as_unread(self):
        self.status = "unread"
        self.save()


class TaskHistory(models.Model):
    task: models.ForeignKey = models.ForeignKey(Task, on_delete=models.CASCADE)
    user: models.ForeignKey = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    action: str = models.CharField(max_length=255)
    timestamp: models.DateTimeField = models.DateTimeField(auto_now_add=True)
    previous_value = models.TextField(null=True, blank=True)

    def __str__(self) -> str:
        return f"History for {self.task.title} by {self.user}"


class TaskComment(models.Model):
    task: models.ForeignKey = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="task_comments_set")
    text: str = models.TextField()
    created_at: models.DateTimeField = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Task comment: {self.text}"


class NotificationSettings(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notification_settings"
    )
    new_task = models.BooleanField(default=True)
    status_change = models.BooleanField(default=True)
    deadline_reminders = models.BooleanField(default=True)

    def __str__(self):
        return f"Notification settings for {self.user}"


class TaskReminder(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="reminders")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    remind_at = models.DateTimeField()
    sent = models.BooleanField(default=False)

    def __str__(self):
        return f"Reminder for {self.task.title} at {self.remind_at}"
