import yaml

from core.configuration.validator import preprocess_config


def get_config(filename="config.yaml"):
    """Loads the configuration file for the pipelines

    :param filename: Filename to look for in the root. If ending is not '.yaml' or '.yml' it will be added
    :type filename: str
    :returns: The configuration entities
    :rtype: dict
    """
    if not filename.endswith(".yaml") and not filename.endswith(".yml"):
        filename += ".yaml"
    with open(filename) as f:
        data = yaml.load(f, Loader=yaml.FullLoader)
    return preprocess_config(data)
