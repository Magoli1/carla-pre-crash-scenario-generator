from xml.etree.ElementTree import Element, SubElement


class Scenario:
    def __init__(self, carla_client):
        self.client = carla_client
        pass

    def get_available_towns(self):
        map_paths = self.client.get_available_maps()
        towns = []
        for map_path in map_paths:
            towns.append(map_path.rsplit('/', 1)[-1])
        return towns

    def generate(self, tree, scenario_type, scenario_name_prefix=None):
        if(scenario_name_prefix is None):
            name_prefix = scenario_type
        root = tree.getroot()
        scenarios = []
        towns = self.get_available_towns()
        for idx, town in enumerate(towns):
            scenario = Element("scenario")
            scenario.set("name", name_prefix + idx)
            scenario.set("type", scenario_type)
            scenario.set("town", town)
        root.extend(scenarios)
