def get_module_class_names(classes):
    """Returns a list of clear-text names of the passed classes

    Eg. <class 'plugins.scenario.Scenario'> will give you 'Scenario'

    :param classes: List of classes
    :type classes: dict
    :returns: Names of the passed classes
    :rtype: list
    """
    return [c.__name__ for c in classes]
