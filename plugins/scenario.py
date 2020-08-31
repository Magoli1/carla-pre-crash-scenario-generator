from xml.etree.ElementTree import Element


class Scenario:
    def __init__(self, carla_client, config, data_provider, step_idx):
        self.client = carla_client
        if "type" not in config:
            raise Exception("Scenario generator property 'type' is mandatory")
        if "name_prefix" not in config:
            config["name_prefix"] = config["type"]
        self.config = config
        self.data_provider = data_provider
        self.step_idx = step_idx

    def generate(self, tree):
        root = tree.getroot()
        scenarios = []
        maps = self.data_provider.get_available_maps_simple_name()
        for idx, town in enumerate(maps):
            scenario = Element("scenario")
            scenario.set("name", f'{self.config["name_prefix"]}{idx}-{self.step_idx}')
            scenario.set("type", self.config["type"])
            scenario.set("town", town)
            scenarios.append(scenario)
        root.extend(scenarios)
