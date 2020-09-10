from xml.etree.ElementTree import Element

from core.helpers.utils import extend_scenarios

class Scenario:
    def __init__(self, carla_client, config, data_provider, step_idx):
        self.client = carla_client
        if "type" not in config:
            raise Exception("Scenario generator property 'type' is mandatory")
        if "name_prefix" not in config:
            config["name_prefix"] = config["type"]
        all_maps = data_provider.get_available_maps_simple_name()
        if "map_blacklist" in config:
            if not isinstance(config["map_blacklist"], list):
                raise Exception("Scenario generator property 'map_blacklist' needs to be a list")
            if not config["map_blacklist"]:
                raise Exception("Scenario generator property 'map_blacklist' is not allowed to be empty")
            is_subset = set(config["map_blacklist"]).issubset(all_maps)
            if not is_subset:
                raise Exception(f'Scenario generator property "map_blacklist" has one value which is not in {all_maps}')
        else:
            config["map_blacklist"] = []
        self.maps = [carla_map for carla_map in all_maps if carla_map not in config["map_blacklist"]]
        self.config = config
        self.data_provider = data_provider
        self.step_idx = step_idx

    def generate(self, tree):
        root = tree.getroot()
        scenarios = []
        for idx, town in enumerate(self.maps):
            scenario = Element("scenario")
            scenario.set("name", f'{self.config["name_prefix"]}{idx}-{self.step_idx}')
            scenario.set("type", self.config["type"])
            scenario.set("town", town)
            scenarios.append(scenario)
        root.extend(scenarios)
