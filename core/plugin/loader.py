import importlib
import pkgutil
import inspect

import plugins

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
        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj) and obj.__module__.startswith("plugins."):
                classes.append(obj)
    return classes

