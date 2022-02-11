from django.core.management import BaseCommand
import digest_backend.digest_executor as digest_executor


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
            digest_executor.check(self)
        if kwargs['setup']:
            digest_executor.setup(self)
        if kwargs['drop']:
            digest_executor.clear(self)
        if kwargs['reset']:
            digest_executor.clear(self)
            digest_executor.setup(self)
        digest_executor.init(self)






