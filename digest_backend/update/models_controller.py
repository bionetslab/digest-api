from typing import Type
from django.db.models import Model


class ModelsController:
    db_model = Model
    db_fields = list()
    db_entries = set()

    def __init__(self, db_model: Type[Model]):
        self.db_model = db_model
        self.db_fields = [f.name for f in db_model._meta.get_fields()]
        self.db_entries = set(db_model.objects.all().values_list('pk', flat=True))

    def get_fields(self) -> list:
        return self.db_fields

    def get_all(self) -> list:
        return self.db_model.objects.all()

    def get_filtered(self, filter_set) -> list:
        return self.db_model.objects.filter(pk=filter_set)

    def create(self, object_dict: dict) -> Model:
        new_obj = self.db_model()
        for key in object_dict:
            setattr(new_obj, key, object_dict[key])
        return new_obj

    def bulk_create(self, object_list: list):
        self.db_model.objects.bulk_create(object_list, batch_size=1000)

    def bulk_update(self, object_list: list):
        self.db_model.objects.bulk_update(object_list, self.db_fields, batch_size=1000)

    def bulk_delete(self, object_list):
        self.db_model.objects.filter(pk__in=object_list).delete()



