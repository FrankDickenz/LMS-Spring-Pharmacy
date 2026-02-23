# your_app/tasks.py
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from courses.models import CourseSessionLog  # Ganti dengan path model Anda
import logging

from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
import smtplib
from django.core.mail import BadHeaderError

logger = logging.getLogger(__name__)

@shared_task
def close_idle_sessions():
    threshold = timezone.now() - timedelta(minutes=30)
    idle_sessions = CourseSessionLog.objects.filter(
        ended_at__isnull=True,
        started_at__lt=threshold
    )
    closed_count = 0
    for session in idle_sessions:
        session.ended_at = timezone.now()
        session.save()  # Ini akan menghitung duration_seconds
        logger.info(f"Auto-closed idle session for user {session.user.id}, course {session.course.id}, duration: {session.duration_seconds} seconds")
        closed_count += 1
    logger.info(f"Closed {closed_count} idle sessions")



@shared_task
def send_invite_email(email, username, course_name):
    subject = f"You have been enrolled in {course_name}"
    message = (
        f"Hello {username},\n\n"
        f"You have been enrolled in the course '{course_name}'.\n"
        f"Please login to access the course.\n\nThanks!"
    )
    try:
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email], fail_silently=False)
        return f"Email sent to {username}"
    except (smtplib.SMTPException, BadHeaderError) as e:
        return f"Email failed for {username}: {e}"