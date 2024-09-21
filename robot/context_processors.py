from robot.models import Notification


def notification_count(request):
    if request.user.is_authenticated:
        notifications_unread = Notification.objects.filter(user=request.user, is_read=False).exists()
        return {'notifications_unread': notifications_unread}
    return {}

