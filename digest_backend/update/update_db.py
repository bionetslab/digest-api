from digest_backend.update.models_controller import ModelsController


def fill_id_table(controller: ModelsController, new_dict: dict, selected_entries=None):
    key_set = new_dict.keys() if selected_entries is None else selected_entries
    add_objects = []
    for key_val in key_set:
        add_objects.append(controller.create(object_dict=new_dict[key_val]))
    controller.bulk_create(object_list=add_objects)


def update_id_table(controller: ModelsController, new_dict: dict):
    all_entry_keys = set(controller.db_model.objects.all().values_list('pk', flat=True))
    # ------------------------------
    # Update entries
    # ------------------------------
    updated_objects = []
    object_list = controller.get_filtered(filter_set=all_entry_keys & new_dict.keys())
    for single_obj in object_list:
        change_made = False
        for field in controller.get_fields():
            if getattr(single_obj, field) != new_dict[single_obj.pk][field]:
                setattr(single_obj, field, new_dict[single_obj.pk][field])
                change_made = True
        if change_made:
            single_obj.save()
            updated_objects.append(single_obj)
    if len(updated_objects) > 0:
        controller.bulk_update(object_list=updated_objects)
    # ------------------------------
    # Delete entries
    # -----------------------------
    outdated_entries = all_entry_keys - new_dict.keys()
    controller.bulk_delete(object_list=outdated_entries)
    # ------------------------------
    # Add entries
    # -----------------------------
    missing_entries = (new_dict.keys() - all_entry_keys)
    fill_id_table(controller=controller, new_dict=new_dict, selected_entries=missing_entries)





