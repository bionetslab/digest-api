from django.core.management import BaseCommand
import digest_backend.digest_executor as executor
from digest_backend import updater



class Command(BaseCommand):


    def add_arguments(self, parser):
        parser.add_argument('-c', '--check', action='store_true', help='Check if setup is necessary and in case execute.')
        parser.add_argument('-s', '--setup', action='store_true', help='Execute setup')
        parser.add_argument('-d', '--drop', action='store_true', help='Remove saved example_files')
        parser.add_argument('-r','--reset',action='store_true',help='Removes saved example_files and executes new setup.')
        parser.add_argument('-i','--scheduler',action='store_true', help='Run the update schedular process')


    def handle(self, *args, **kwargs):
        if kwargs['scheduler']:
            updater.start()
        if kwargs['check']:
            executor.check()
        if kwargs['setup']:
            executor.setup()
        if kwargs['drop']:
            executor.clear()
        if kwargs['reset']:
            executor.clear()
            executor.setup()






