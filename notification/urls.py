#urls.py notification app
from django.urls import path
from . import views

app_name = "notification"

urlpatterns = [
    # contoh route
    path('notif', views.notification_list, name='notification_list'),
    path('read/<int:notif_id>/', views.mark_as_read, name='mark_as_read'),
]