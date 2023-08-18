import os

from celery import Celery
from celery.schedules import crontab
from django.conf import settings


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "blog.settings")

app = Celery("blog")

app.config_from_object(settings, namespace="CELERY")

app.autodiscover_tasks()

app.conf.beat_schedule = {
    "delete_unverified_users": {
        "task": "accounts.tasks.delete_unverified_users",
        "schedule": crontab(day_of_week="*", hour=0, minute=0),
    },
}
