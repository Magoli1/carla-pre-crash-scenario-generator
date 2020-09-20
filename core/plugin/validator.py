import inspect

from core.plugin.utils import get_module_class_names, get_implemented_class_functions
from core.helpers.utils import get_duplicates


def check_plugins(classes):
    """Checks the plugins classes for implementation errors

    :param classes: List of (Python) classes
    :type classes: list
    """
    class_names = get_module_class_names(classes)
    check_duplicate_class_names(class_names)
    for _class in classes:
        check_implemented_functions(_class)


def check_duplicate_class_names(class_names):
    """Raises an exception if there are duplicates in the given class names

    :param class_names: List of class names
    :type class_names: list
    """
    duplicates = get_duplicates(class_names)
    if duplicates:
        raise Exception(
            f'Only globally unique class names are allowed. Found duplicates {duplicates}')


def check_implemented_functions(_class):
    """Raises an exception if the passed class has not implemented the mandatory methods

    :param _class: Class to check
    :type _class: object
    """
    mandatory_functions_to_implement = [('generate', 2), ('__init__', 5)]
    implemented_class_function_names = get_implemented_class_functions(_class)
    for function in mandatory_functions_to_implement:
        function_name = function[0]
        number_function_mandatory_params = function[1]
        # check if the method is implemented in the class
        if function_name not in implemented_class_function_names:
            raise Exception(f"Method {function_name} not implemented in class {_class.__name__}")
        ref_function = getattr(_class, function_name)
        # check if the method is expecting the mandatory number of arguments
        if not len(inspect.getfullargspec(ref_function).args) == number_function_mandatory_params:
            raise Exception(
                f"Method {function_name} implemented in class {_class.__name__} is not expecting {number_function_mandatory_params} passed arguments")
