import importlib
import pkgutil
import inspect

import plugins
from core.configuration.utils import get_pipeline_step_names


def iter_namespace(ns_pkg):
    # source https://packaging.python.org/guides/creating-and-discovering-plugins/
    # Specifying the second argument (prefix) to iter_modules makes the
    # returned name an absolute name instead of a relative one. This allows
    # import_module to work without having to do additional modification to
    # the name.
    return pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + ".")


discovered_plugins = {
    name: importlib.import_module(name)
    for finder, name, ispkg
    in iter_namespace(plugins)
}


def get_plugin_classes():
    classes = []
    for _, module in discovered_plugins.items():
        for _, obj in inspect.getmembers(module):
            if inspect.isclass(obj) and obj.__module__.startswith("plugins."):
                classes.append(obj)
    return classes


def get_plugin_classes_in_configured_order(pipeline_config):
    # gets the plugin classes in configured order
    classes = get_plugin_classes()
    class_names = get_module_class_names(classes)
    classes_in_order = []
    pipeline_step_names = get_pipeline_step_names(pipeline_config)
    for class_name in pipeline_step_names:
        idx = class_names.index(class_name)
        classes_in_order.append(classes[idx])
    return classes_in_order


def get_module_class_names(classes):
    # get class name of classes
    # eg. <class 'plugins.scenario.Scenario'> will give you Scenario
    return [c.__name__ for c in classes]
