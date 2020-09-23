from xml.etree.ElementTree import SubElement

from core.helpers.utils import extend_scenarios

import random


class Actor:
    def __init__(self, carla_client, config, data_provider, step_idx):
        self.client = carla_client
        if "type" not in config:
            config["type"] = "vehicle"
        self.actor_models = [actor.id for actor in
                             self.client.get_world().get_blueprint_library().filter(
                                 config["type"])]
        self.actor_models.remove('vehicle.bh.crossbike')

        if "tag" not in config:
            config["tag"] = "ego_vehicle"
        if config["tag"] not in ["ego_vehicle", "other_actor"]:
            raise Exception(
                "Actor generators optional property 'tag' must be in ['ego_vehicle', 'other_actor']")
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
        if not pos_config["streets"] and not pos_config["junctions"]:
            raise Exception(
                "Actor generators optional properties 'streets' and 'junctions' cannot both be 'False'")
        self.config = config
        self.data_provider = data_provider
        self.step_idx = step_idx

    def generate(self, tree):
        extend_scenarios(tree, self.config["per_scenario"] - 1, self.step_idx)
        for scenario in tree.getroot().getchildren():
            actor = SubElement(scenario, self.config["tag"])
            attributes = {}
            attributes["waypoint"] = random.choice(
                self.get_allowed_waypoints_in_town(scenario.get("town")))
            attributes["actor_model"] = random.choice(self.actor_models)
            self.decorate_actor(actor, **attributes)

    def get_allowed_waypoints_in_town(self, town_name):
        pos_config = self.config["positioning"]
        waypoints_in_town = self.data_provider.get_waypoints_per_map()[town_name]
        allowed_waypoints = []
        if pos_config["junctions"]:
            allowed_waypoints += waypoints_in_town["junctions"]
        if pos_config["streets"]:
            allowed_waypoints += waypoints_in_town["streets"]
        return allowed_waypoints

    def decorate_actor(self, actor, **kwargs):
        if "waypoint" in kwargs:
            actor.set("x", str(round(kwargs["waypoint"].transform.location.x, 2)))
            actor.set("y", str(round(kwargs["waypoint"].transform.location.y, 2)))
            actor.set("z", str(round(kwargs["waypoint"].transform.location.z, 2)))
            actor.set("yaw", str(round(kwargs["waypoint"].transform.rotation.yaw, 2)))

        if "actor_model" in kwargs:
            actor.set("model", kwargs["actor_model"])
        pass
