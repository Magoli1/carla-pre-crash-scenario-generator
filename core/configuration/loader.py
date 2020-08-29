import yaml

from core.configuration.validator import check_valid_config


def get_config(filename="config.yaml"):
    if not filename.endswith(".yaml") and not filename.endswith(".yml"):
        filename += ".yaml"
    with open(filename) as f:
        data = yaml.load(f, Loader=yaml.FullLoader)
    return check_valid_config(data)
