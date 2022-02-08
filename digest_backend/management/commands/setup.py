from django.core.management import BaseCommand

def setup(self):
    pass


def check(self):
    if True :
        setup(self)

def clear(self):
    pass


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('-c', '--check', action='store_true', help='Check if setup is necessary and in case execute.')
        parser.add_argument('-s', '--setup', action='store_true', help='Execute setup')
        parser.add_argument('-d', '--drop', action='store_true', help='Remove saved data')
        parser.add_argument('-r','--reset',action='store_true',help='Removes saved data and executes new setup.')

    def handle(self, *args, **kwargs):
        if kwargs['check']:
            check(self)
        if kwargs['setup']:
            setup(self)
        if kwargs['drop']:
            clear(self)
        if kwargs['reset']:
            clear(self)
            setup(self)




