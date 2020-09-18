import importlib
import pkgutil
import inspect

import plugins
from core.configuration.utils import get_pipeline_step_names
from core.plugin.utils import get_module_class_names
from core.plugin.validator import check_plugins


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
    """Returns all classes contained in the plugin directory

    :returns: All classes which are declared in the files in the plugin directory
    :rtype: list
    """
    classes = []
    for _, module in discovered_plugins.items():
        for _, obj in inspect.getmembers(module):
            if inspect.isclass(obj) and obj.__module__.startswith("plugins."):
                classes.append(obj)
    check_plugins(classes)
    return classes


def get_plugin_classes_in_configured_order(pipeline_config):
    """Returns all classes in the plugin directory in configured order

    :param pipeline_config: Pipelines configuration entity
    :type pipeline_config: dict
    :returns: All classes which are declared in the files in the plugin directory in the configured order of the generator config
    :rtype: list
    """
    classes = get_plugin_classes()
    class_names = get_module_class_names(classes)
    classes_in_order = []
    pipeline_step_names = get_pipeline_step_names(pipeline_config)
    for class_name in pipeline_step_names:
        idx = class_names.index(class_name)
        classes_in_order.append(classes[idx])
    return classes_in_order
