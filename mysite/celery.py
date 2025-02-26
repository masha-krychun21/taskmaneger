import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")

from celery import Celery

django.setup()

# from polls.signals import send_task_reminders


app = Celery("mysite")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
app.conf.worker_concurrency = 1
app.conf.update(
    task_always_eager=False,
    worker_pool="solo",
    broker_url="redis://redis:6379/0",
    result_backend="redis://redis:6379/0",
)
app.conf.enable_utc = True
app.conf.timezone = "UTC"
