from core.plugin.loader import get_plugin_classes, get_module_class_names
from core.configuration.utils import get_pipeline_step_names, extract_pipeline_config, \
    extract_pipeline_name
from core.helpers.utils import get_duplicates
from core.logger.logger import logger


def set_default_values(config):
    """Sets default values for all necessary values of the generator config

    :param config: Generator configuration entity
    :type config: dict
    :returns: The configuration with set default values
    :rtype: dict
    """
    if "dataprovider" not in config:
        config["dataprovider"] = {"preload": False}
    if "preload" not in config["dataprovider"]:
        config["dataprovider"]["preload"] = False
    return config


def preprocess_config(config):
    """Preprocesses the configuration of the generator for missing attributes

    :param config: Generator configuration entity
    :type config: dict
    :returns: The checked configuration with set default values
    :rtype: dict
    """
    if "pipelines" not in config:
        logger.error("Config error: Mandatory 'pipelines' key not found in config")
        raise SystemExit(0)
    check_pipelines_config(config["pipelines"])
    if "dataprovider" in config:
        check_data_provider_config_valid(config["dataprovider"])
    return set_default_values(config)


def check_pipelines_config(pipelines_config):
    """Checks the configuration of a pipeline for validity

    :param pipelines_config: Pipeline configuration entity
    :type pipelines_config: dict
    """
    if not isinstance(pipelines_config, list):
        logger.error("Config error: 'pipelines' value needs to be a list")
        raise SystemExit(0)
    check_duplicate_pipeline_names(pipelines_config)
    for idx, pipeline in enumerate(pipelines_config):
        pipeline_config = extract_pipeline_config(pipeline)
        check_pipeline_config_valid(idx + 1, pipeline_config)


def check_duplicate_pipeline_names(pipelines_config):
    """Checks the configuration of all pipelines for duplicated names

    :param pipelines_config: Pipelines configuration entity
    :type pipelines_config: dict
    """
    pipeline_names = [extract_pipeline_name(pipeline) for pipeline in pipelines_config]
    duplicates = get_duplicates(pipeline_names)
    if duplicates:
        logger.error(
            f'Only globally unique pipeline names are allowed. Found duplicates {duplicates}')
        raise SystemExit(0)


def check_pipeline_config_valid(idx, pipeline_config):
    """Checks all the configuration entities of a pipeline

    :param idx: Index of the pipeline step. Used for logging
    :type idx: int
    :param pipeline_config: Pipeline configuration entity
    :type pipeline_config: dict
    """
    if not isinstance(pipeline_config, dict):
        logger.error(f'Config error at pipeline #{idx}: "pipeline" entity needs to be a dict')
        raise SystemExit(0)
    if "steps" not in pipeline_config:
        logger.error(f'Config error at pipeline #{idx}: "steps" value is missing')
        raise SystemExit(0)
    check_steps_config_valid(idx, pipeline_config["steps"])


def check_data_provider_config_valid(data_provider_config):
    """Checks the data provider configuration entity for validity

    :param data_provider_config: Configuration entity of the data provider
    :type data_provider_config: dict
    """
    if not isinstance(data_provider_config, dict):
        logger.error("Config error: 'dataprovider' value needs to be a dictionary")
        raise SystemExit(0)
    if "preload" in data_provider_config and not isinstance(data_provider_config["preload"], bool):
        logger.error("Config error: 'dataprovider:preload' value needs to be a boolean")
        raise SystemExit(0)


def check_steps_config_valid(idx, steps_config):
    """Checks the steps of the pipeline configuration for validity

    :param idx: Index of the pipeline step. Used for logging
    :type idx: int
    :param steps_config: Steps configuration entity of the pipeline
    :type steps_config: dict
    """
    if not isinstance(steps_config, list):
        logger.error(f'Config error at pipeline #{idx}: "steps" value needs to be a list')
        raise SystemExit(0)
    # check if all configured pipeline steps actually exist via a class in the plugins section
    classes = get_plugin_classes()
    class_names = get_module_class_names(classes)
    pipeline_step_names = get_pipeline_step_names(steps_config)
    is_subset = set(pipeline_step_names).issubset(class_names)
    if not is_subset:
        logger.error(
            f'Config error at pipeline #{idx}: '
            f'One or more of the configured steps do not correspond to a valid class name.'
            f' Value needs to be in {class_names}')
        raise SystemExit(0)
