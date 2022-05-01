from django.core.management import BaseCommand
import digest_backend.digest_executor as executor


from django.apps import AppConfig
from digest_backend import updater


class RoomConfig(AppConfig):
    name = 'digest'

    def ready(self):
        from digest_backend import updater
        updater.start()

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('-c', '--check', action='store_true', help='Check if setup is necessary and in case execute.')
        parser.add_argument('-s', '--setup', action='store_true', help='Execute setup')
        parser.add_argument('-d', '--drop', action='store_true', help='Remove saved example_files')
        parser.add_argument('-r','--reset',action='store_true',help='Removes saved example_files and executes new setup.')

    def handle(self, *args, **kwargs):
        if kwargs['check']:
            executor.check()
            # digest_executor.check()
        if kwargs['setup']:
            executor.setup()
        if kwargs['drop']:
            executor.clear()
        if kwargs['reset']:
            executor.clear()
            executor.setup()

        updater.start()






