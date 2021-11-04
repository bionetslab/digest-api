from django.core.management import BaseCommand

from digest_backend.update.models_controller import ModelsController
from digest_backend.update import update_db
from digest_backend.models import Example


class DatabaseHandler:
    def load_data(self, count):
        print("Loading test data...")
        for i in range(0, count):
            Example.objects.update_or_create(name=f'Example{i}', count=i)
        print(f'Added {count} entries to test data table')

    def update_data(self, count):
        print("Loading test data...")
        test_data = dict()
        for i in range(5, count):
            test_data[f'Example{i}'] = {'name': f'Example{i}', 'count': i}
        mc = ModelsController(db_model=Example)
        update_db.update_id_table(controller=mc, new_dict=test_data)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('-r', '--refill', action='store_true', help='Refill database')
        parser.add_argument('-u', '--update', action='store_true', help='Update database')

    def handle(self, *args, **kwargs):
        handler = DatabaseHandler()
        if kwargs['refill']:
            handler.load_data(5)
        if kwargs['update']:
            handler.update_data(11)



