from xml.etree.ElementTree import Element


class Scenario:
    def __init__(self, carla_client, config):
        self.client = carla_client
        if "type" not in config:
            raise Exception("Scenario generator property 'type' is mandatory")
        if "name_prefix" not in config:
            config["name_prefix"] = config["type"]
        self.config = config

    def get_available_towns(self):
        map_paths = self.client.get_available_maps()
        towns = []
        for map_path in map_paths:
            towns.append(map_path.rsplit('/')[-1])
        return towns

    def generate(self, tree):
        root = tree.getroot()
        scenarios = []
        towns = self.get_available_towns()
        for idx, town in enumerate(towns):
            scenario = Element("scenario")
            scenario.set("name", f'{self.config["name_prefix"]}{idx}')
            scenario.set("type", self.config["type"])
            scenario.set("town", town)
            scenarios.append(scenario)
        root.extend(scenarios)
