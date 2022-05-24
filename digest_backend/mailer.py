from celery import shared_task
from celery.utils.log import get_task_logger
from django.core.mail import send_mail
from digest_backend.models import Notification, Task



logger = get_task_logger(__name__)

@shared_task
def check_mails():
    logger.info("Checking for mails to send...")
    to_remove = set()
    uids = set()
    for n in Notification.objects.all():
        if n.uid not in uids:
            uids.add(n.uid)
    for uid in uids:
        t=Task.objects.get(uid= uid)
        if t.sc_done:
            to_remove.add(uid)
            logger.info(f"Sending mails for task {uid}")
            send_notification(uid)



def send_test_mail(arg):
    send_mail('Celery scheduler test mail',
              f'Celery is running',
              'info@digest-validation.net', ['andi.majore@googlemail.com'], fail_silently=False)


def get_notification_mails(id):
    try:
        mails = []
        for n in Notification.objects.filter(uid=id):
            mails.append(n.mail)
        return mails
    except Exception:
        print("No mailing entries fround for ID="+id)
        return None


def send_notification(id):
    mails = get_notification_mails(id)
    if mails is not None:
        link = "https://digest-validation.net/result?id="+id
        send_mail('Your job has finished',f'The contribution signficance calculation for your digest-validation job has terminated.\nCheck them out here: {link}', 'info@digest-validation.net',mails, fail_silently=True)
        remove_notification(id)

def remove_notification(id):
    # try:
        for n in Notification.objects.filter(uid=id):
            n.delete()
    # except:
    #     pass

def server_startup():
    send_mail('Digest-validation system startup', f'The digest-validation backend is now ready!', 'info@digest-validation.net', ['andi.majore@googlemail.com'], fail_silently=False)