from core.plugin.loader import get_plugin_classes, get_module_class_names
from core.configuration.utils import get_pipeline_step_names, get_duplicates


def set_default_values(config):
    if "preload" not in config["dataprovider"]:
        config["dataprovider"]["preload"] = False
    return config


def check_valid_config(config):
    # checks the configuration file for missing entities
    if "pipeline" not in config:
        raise Exception("Config error: Mandatory 'pipeline' key not found in config")
    check_pipeline_config_valid(config["pipeline"])
    check_data_provider_config_valid(config["dataprovider"])
    return set_default_values(config)


def check_data_provider_config_valid(data_provider_config):
    if not isinstance(data_provider_config, dict):
        raise Exception("Config error: 'dataprovider' value needs to be a dictionary")
    if "preload" in data_provider_config and not isinstance(data_provider_config["preload"], bool):
        raise Exception("Config error: 'dataprovider:preload' value needs to be a boolean")


def check_pipeline_config_valid(pipeline_config):
    if not isinstance(pipeline_config, list):
        raise Exception("Config error: 'pipeline' value needs to be a list")
    # check if all configured pipeline steps actually exist via a class in the plugins section
    classes = get_plugin_classes()
    class_names = get_module_class_names(classes)
    check_duplicate_class_names(class_names)
    pipeline_step_names = get_pipeline_step_names(pipeline_config)
    is_subset = set(pipeline_step_names).issubset(class_names)
    if not is_subset:
        raise Exception(
            "One or more of the configured pipeline steps do not correspond to a valid class name")


def check_duplicate_class_names(class_names):
    duplicates = get_duplicates(class_names)
    if duplicates:
        raise Exception(
            f'Only globally unique class names are allowed. Found duplicates {duplicates}')
