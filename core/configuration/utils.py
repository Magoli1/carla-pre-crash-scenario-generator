from core.logger.logger import logger


def get_pipeline_step_names(step_config):
    """Extracts the step names from the configured steps of a pipeline

    :param step_config: Step configuration of a pipeline
    :type step_config: dict
    :returns: The names of the steps
    :rtype: list
    """
    step_names = []
    for step in step_config:
        if isinstance(step, dict):
            step_names.append(list(step.keys())[0])
        elif isinstance(step, str):
            step_names.append(step)
        else:
            logger.error("Pipeline config not valid")
            raise SystemExit(0)
    return step_names


def extract_pipeline_name(pipeline):
    """Extracts the name of a configured pipeline

    :param pipeline: Pipeline configuration entity
    :type pipeline: dict
    :returns: The name of the given pipeline
    :rtype: str
    """
    return list(pipeline.keys())[0]


def extract_pipeline_config(pipeline):
    """Extracts the configuration entities of a pipeline

    :param pipeline: Pipeline configuration entity
    :type pipeline: dict
    :returns: The configuration entities of pipeline
    :rtype: dict
    """
    return list(pipeline.values())[0]
