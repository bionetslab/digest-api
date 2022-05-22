from django.core.mail import send_mail
from digest_backend.models import Notification

def get_notification_mails(id):
    try:
        mails = []
        for n in Notification.objects.filter(uid=id):
            mails.append(n.mail)
        return mails
    except Exception:
        return None


def send_notification(id):
    mails = get_notification_mails(id)
    if mails is not None:
        link = "https://digest-validation.net/result?id="+id
        send_mail('Your job has finished',f'The contribution signficance calculation for your digest-validation job has terminated.<br>Check them out here: {link}', 'info@digest-validation.net',mails, fail_silently=True)
        remove_notification(id)

def remove_notification(id):
    try:
        for n in get_notification_mails(id):
            n.delete()
    except:
        pass

def server_startup():
    send_mail('Digest-validation system startup', f'The digest-validation backend is now ready!', 'info@digest-validation.net', ['andi.majore@googlemail.com'], fail_silently=False)