from core.plugin.utils import get_module_class_names
from core.helpers.utils import get_duplicates


def check_plugins(classes):
    class_names = get_module_class_names(classes)
    check_duplicate_class_names(class_names)


def check_duplicate_class_names(class_names):
    duplicates = get_duplicates(class_names)
    if duplicates:
        raise Exception(
            f'Only globally unique class names are allowed. Found duplicates {duplicates}')
