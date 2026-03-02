from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from .models import Notification


def index(request):
    return HttpResponse("Notification app works!")


@login_required
def notification_list(request):
    notifications = (
        Notification.objects
        .filter(user=request.user)
        .order_by('-created_at')
    )

    paginator = Paginator(notifications, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        'notifications/list.html',
        {'notifications': page_obj}
    )


@login_required
def mark_as_read(request, notif_id):
    notif = get_object_or_404(
        Notification,
        id=notif_id,
        user=request.user
    )

    if not notif.is_read:
        notif.is_read = True
        notif.save(update_fields=['is_read'])

    if notif.link:
        return redirect(notif.link)

    return redirect('notification:notification_list')