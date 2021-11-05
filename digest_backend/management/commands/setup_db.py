from django.core.management import BaseCommand

from digest_backend.update.models_controller import ModelsController
from digest_backend.update import update_db
from digest_backend.models import Example


class DatabaseHandler:
    def load_data(self, count):
        self.drop_data()  # make sure that database is empty
        print("Loading test data...")
        test_data = dict()
        for i in range(0, count):
            test_data[f'Example{i}'] = {'name': f'Example{i}', 'count': i}
        mc = ModelsController(db_model=Example)
        update_db.fill_id_table(controller=mc, new_dict=test_data)
        print(f'Added {count} entries to test data table')

    def update_data(self, count):
        print("Loading test data...")
        test_data = dict()
        for i in range(5, count):
            test_data[f'Example{i}'] = {'name': f'Example{i}', 'count': i}
        mc = ModelsController(db_model=Example)
        update_db.update_id_table(controller=mc, new_dict=test_data)

    def drop_data(self):
        print("Droping test data...")
        Example.objects.all().delete()


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('-r', '--refill', action='store_true', help='Refill database')
        parser.add_argument('-u', '--update', action='store_true', help='Update database')
        parser.add_argument('-d', '--drop', action='store_true', help='Drop all entries in database')

    def handle(self, *args, **kwargs):
        handler = DatabaseHandler()
        if kwargs['refill']:
            handler.load_data(5)
        if kwargs['update']:
            handler.update_data(11)
        if kwargs['drop']:
            handler.drop_data()



