from django.core.management import BaseCommand
import digest_backend.digest_executor as executor
from digest_backend.mailer import server_startup


class Command(BaseCommand):


    def add_arguments(self, parser):
        parser.add_argument('-c', '--check', action='store_true', help='Check if setup is necessary and in case execute.')
        parser.add_argument('-s', '--setup', action='store_true', help='Execute setup')
        parser.add_argument('-d', '--drop', action='store_true', help='Remove saved example_files')
        parser.add_argument('-r','--reset',action='store_true',help='Removes saved example_files and executes new setup.')
        parser.add_argument('-e','--examples',action='store_true',help='Precompute example case validations.')

    def handle(self, *args, **kwargs):
        if kwargs['check']:
            executor.check()
        if kwargs['setup']:
            executor.setup()
        if kwargs['drop']:
            executor.clear()
        if kwargs['reset']:
            executor.clear()
            executor.setup()
        if kwargs['examples']:
            executor.precompute_examples()
        server_startup()






