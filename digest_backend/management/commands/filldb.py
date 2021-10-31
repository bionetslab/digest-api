from django.core.management import BaseCommand

from digest_backend.models import Example


class DatabaseHandler:
    def load_test_data(self, count):
        print("Loading test data...")
        for i in range(0,count):
            Example.objects.update_or_create(name=f'Example{i}', count=i)
        print(f'Added {count} entries to test data table')


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('-t', '--test', type=int, help='Add test data to the database')

    def handle(self, *args, **kwargs):
        handler = DatabaseHandler()
        if kwargs['test'] is not None:
            handler.load_test_data(int(kwargs['test']))


