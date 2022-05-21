from django.core.mail import send_mail
from digest_backend.models import Notification

def get_notification_mail(id):
    try:
        return Notification.objects.get(uid=id)
    except Exception:
        return None


def send_notification(id):
    n = get_notification_mail(id)
    if n is not None:
        link = "https://digest-validation.net/result?id="+id
        send_mail('Your job has finished',f'The contribution signficance calculation for your digest-validation job has terminated.<br>Check them out here: {link}', 'info@digest-validation.net',[n.mail], fail_silently=True)
        remove_notification(id)

def remove_notification(id):
    try:
        get_notification_mail(id).delete()
    except:
        pass

def server_startup():
    send_mail('Digest-validation system startup', f'The digest-validation backend is now ready!', 'info@digest-validation.net', ['andi.majore@googlemail.com'], fail_silently=False)