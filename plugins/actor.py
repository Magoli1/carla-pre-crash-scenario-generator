from xml.etree.ElementTree import SubElement

from core.helpers.utils import extend_scenarios

class Actor:
    def __init__(self, carla_client, config, data_provider):
        self.client = carla_client
        if "tag" not in config:
            config["tag"] = "ego_vehicle"
        if "per_scenario" not in config:
            config["per_scenario"] = 1
        if config["per_scenario"] <= 0:
            raise Exception("Actor generators optional property 'per_scenario' cannot be <= 0")
        if "positioning" not in config:
            config["positioning"] = {"junctions": True, "streets": True, "distance_between": 5}
        pos_config = config["positioning"]
        if "junctions" not in pos_config:
            pos_config["junctions"] = True
        if "streets" not in pos_config:
            pos_config["streets"] = True
        self.config = config
        self.data_provider = data_provider

    def generate(self, tree):
        extend_scenarios(tree, self.config["per_scenario"] - 1)
        for scenario in tree.getroot().getchildren():
            actor = SubElement(scenario, self.config["tag"])
            self.generate_actor(actor)

    def generate_actor(self, actor):
        waypoints = self.data_provider.get_waypoints_per_map()
        
        print(waypoints["Town01"])
        transform.location -> xyz
        transform.rotation -> yaw
        pass
