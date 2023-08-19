from datetime import datetime, timedelta

from celery import shared_task
from django.contrib.auth import get_user_model

from .utils import send_email_for_reset_password, send_email_for_verification


User = get_user_model()


@shared_task()
def send_task_for_verification_email(user_id, receiver, current_site, mail_subject, email_template):
    send_email_for_verification(user_id, receiver, current_site, mail_subject, email_template)
    return 'Completed'


@shared_task()
def send_task_for_reset_password(user_id, receiver, current_site, mail_subject, email_template):
    send_email_for_reset_password(user_id, receiver, current_site, mail_subject, email_template)
    return 'Completed'


@shared_task
def delete_unverified_users():
    one_week_ago = datetime.now() - timedelta(days=7)
    unverified_users = User.objects.filter(created_date__lt=one_week_ago, is_verified=False)
    unverified_users.delete()
