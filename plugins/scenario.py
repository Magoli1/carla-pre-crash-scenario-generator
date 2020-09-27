from xml.etree.ElementTree import Element

from core.helpers.utils import extend_scenarios


class Scenario:
    def __init__(self, carla_client, config, data_provider, step_idx, logger):
        self.client = carla_client
        self.logger = logger
        if "type" not in config:
            self.logger.error("Scenario generator property 'type' is mandatory")
            raise SystemExit(0)
        if "name_prefix" not in config:
            config["name_prefix"] = config["type"]
        all_maps = data_provider.get_available_maps_simple_name()
        if "map_blacklist" in config:
            if not isinstance(config["map_blacklist"], list):
                self.logger.error("Scenario generator property 'map_blacklist' needs to be a list")
                raise SystemExit(0)
            if not config["map_blacklist"]:
                self.logger.error(
                    "Scenario generator property 'map_blacklist' is not allowed to be empty")
                raise SystemExit(0)
            is_subset = set(config["map_blacklist"]).issubset(all_maps)
            if not is_subset:
                self.logger.error(
                    f'Scenario generator property "map_blacklist" '
                    f'has one value which is not in {all_maps}')
                raise SystemExit(0)
        else:
            config["map_blacklist"] = []
        self.maps = [carla_map for carla_map in all_maps if
                     carla_map not in config["map_blacklist"]]
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
