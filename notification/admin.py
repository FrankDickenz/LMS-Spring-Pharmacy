from django.contrib import admin
from .models import Notification

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'user', 'actor', 'notif_type', 'priority', 'is_read', 'created_at')
    list_filter = ('is_read', 'priority', 'notif_type', 'created_at')
    search_fields = ('title', 'message', 'user__username', 'actor__username')
    readonly_fields = ('created_at',)
    actions = ['mark_selected_as_read']

    list_per_page = 25  # Menampilkan 25 notifikasi per halaman

    def mark_selected_as_read(self, request, queryset):
        updated = queryset.update(is_read=True)
        self.message_user(request, f"{updated} notifikasi telah ditandai sebagai dibaca.")
    mark_selected_as_read.short_description = "Tandai notifikasi terpilih sebagai dibaca"