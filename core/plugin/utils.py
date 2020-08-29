def get_module_class_names(classes):
    # get class name of classes
    # eg. <class 'plugins.scenario.Scenario'> will give you Scenario
    return [c.__name__ for c in classes]
