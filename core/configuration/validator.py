from core.plugin.loader import get_plugin_classes, get_module_class_names
from core.configuration.utils import get_pipeline_step_names, extract_pipeline_config, \
    extract_pipeline_name
from core.helpers.utils import get_duplicates


def set_default_values(config):
    if "dataprovider" not in config:
        config["dataprovider"] = {"preload": False}
    if "preload" not in config["dataprovider"]:
        config["dataprovider"]["preload"] = False
    return config


def check_valid_config(config):
    # checks the configuration file for missing entities
    if "pipelines" not in config:
        raise Exception("Config error: Mandatory 'pipelines' key not found in config")
    check_pipelines_config(config["pipelines"])
    if "dataprovider" in config:
        check_data_provider_config_valid(config["dataprovider"])
    return set_default_values(config)


def check_pipelines_config(pipelines_config):
    if not isinstance(pipelines_config, list):
        raise Exception("Config error: 'pipelines' value needs to be a list")
    check_duplicate_pipeline_names(pipelines_config)
    for idx, pipeline in enumerate(pipelines_config):
        pipeline_config = extract_pipeline_config(pipeline)
        check_pipeline_config_valid(idx + 1, pipeline_config)


def check_duplicate_pipeline_names(pipelines_config):
    pipeline_names = [extract_pipeline_name(pipeline) for pipeline in pipelines_config]
    duplicates = get_duplicates(pipeline_names)
    if duplicates:
        raise Exception(
            f'Only globally unique pipeline names are allowed. Found duplicates {duplicates}')


def check_pipeline_config_valid(idx, pipeline_config):
    if not isinstance(pipeline_config, dict):
        raise Exception(f'Config error at pipeline #{idx}: "pipeline" entity needs to be a dict')
    if "steps" not in pipeline_config:
        raise Exception(f'Config error at pipeline #{idx}: "steps" value is missing')
    check_steps_config_valid(idx, pipeline_config["steps"])


def check_data_provider_config_valid(data_provider_config):
    if not isinstance(data_provider_config, dict):
        raise Exception("Config error: 'dataprovider' value needs to be a dictionary")
    if "preload" in data_provider_config and not isinstance(data_provider_config["preload"], bool):
        raise Exception("Config error: 'dataprovider:preload' value needs to be a boolean")


def check_steps_config_valid(idx, steps_config):
    if not isinstance(steps_config, list):
        raise Exception(f'Config error at pipeline #{idx}: "steps" value needs to be a list')
    # check if all configured pipeline steps actually exist via a class in the plugins section
    classes = get_plugin_classes()
    class_names = get_module_class_names(classes)
    pipeline_step_names = get_pipeline_step_names(steps_config)
    is_subset = set(pipeline_step_names).issubset(class_names)
    if not is_subset:
        raise Exception(
            f'Config error at pipeline #{idx}: One or more of the configured steps do not correspond to a valid class name. Value needs to be in {class_names}')
