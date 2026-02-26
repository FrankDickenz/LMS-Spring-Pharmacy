# notification/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if self.scope["user"].is_anonymous:
            await self.close()
            return

        self.user = self.scope["user"]
        self.group_name = f"user_{self.user.id}"   # group personal per user

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

        # Optional: kirim unread count saat connect
        unread_count = await self.get_unread_count()
        await self.send(text_data=json.dumps({
            'type': 'unread_count',
            'count': unread_count
        }))

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )

    # Method dipanggil saat ada pesan dari backend
    async def send_notification(self, event):
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'id': event['id'],
            'notif_type': event['notif_type'],
            'title': event['title'],
            'message': event['message'],
            'link': event['link'],
            'created_at': event['created_at'].isoformat(),
            'actor_username': event.get('actor_username'),
        }))

    @database_sync_to_async
    def get_unread_count(self):
        from .models import Notification
        return Notification.objects.filter(user=self.user, is_read=False).count()