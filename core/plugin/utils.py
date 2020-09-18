def get_module_class_names(classes):
    """Returns a list of clear-text names of the passed classes

    Eg. <class 'plugins.scenario.Scenario'> will give you 'Scenario'

    :param classes: List of classes
    :type classes: dict
    :returns: Names of the passed classes
    :rtype: list
    """
    return [c.__name__ for c in classes]


def get_implemented_class_functions(_class):
    """Returns a list of implemented functions of a class (with internal methods starting with '__')

    :param _class: Class from where to get the methods
    :type _class: object
    :returns: Names of methods implemented in the passed class
    :rtype: list
    """
    return [func for func in dir(_class) if callable(getattr(_class, func))]
