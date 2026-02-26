# notifications/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json

from .models import Notification


@receiver(post_save, sender=Notification)
def send_real_time_notification(sender, instance, created, **kwargs):
    if not created:
        return  # hanya kirim saat baru dibuat

    channel_layer = get_channel_layer()

    payload = {
        'type': 'send_notification',   # nama method di consumer
        'id': instance.id,
        'notif_type': instance.notif_type,
        'title': instance.title,
        'message': instance.message,
        'link': instance.link,
        'created_at': instance.created_at.isoformat(),
        'actor_username': instance.actor.username if instance.actor else None,
    }

    async_to_sync(channel_layer.group_send)(
        f"user_{instance.user.id}",
        payload
    )