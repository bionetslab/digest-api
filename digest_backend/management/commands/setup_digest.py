from django.core.management import BaseCommand
import digest_backend.digest_executor as executor
from django.core.cache import cache


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('-c', '--check', action='store_true', help='Check if setup is necessary and in case execute.')
        parser.add_argument('-s', '--setup', action='store_true', help='Execute setup')
        parser.add_argument('-d', '--drop', action='store_true', help='Remove saved data')
        parser.add_argument('-r','--reset',action='store_true',help='Removes saved data and executes new setup.')

    def handle(self, *args, **kwargs):
        print("reading commands")
        if kwargs['check']:
            print("checking")
            executor.check()
            # digest_executor.check()
        if kwargs['setup']:
            executor.setup()
        if kwargs['drop']:
            executor.clear()
        if kwargs['reset']:
            executor.clear()
            executor.setup()
        executor.init()






