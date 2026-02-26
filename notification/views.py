# views.py notification app
from django.shortcuts import render
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponse
from .models import Notification
from django.core.paginator import Paginator

def index(request):
    return HttpResponse("Notification app works!")
def notification_list(request):
    user = request.user
    notifications = Notification.objects.filter(user=user).order_by('-created_at')
    paginator = Paginator(notifications, 20)  # 20 per halaman
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'notifications/list.html', {'notifications': page_obj})

def mark_as_read(request, notif_id):
    notif = get_object_or_404(Notification, id=notif_id, user=request.user)
    notif.is_read = True
    notif.save(update_fields=['is_read'])
    
    # Jika notif punya link, redirect ke situ, kalau tidak, kembali ke list
    if notif.link:
        return redirect(notif.link)
    return redirect('notification:notification_list')