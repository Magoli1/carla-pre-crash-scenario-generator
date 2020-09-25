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
            config["positioning"] = {"junctions": {"straight": True, "left": True, "right": True},
                                     "streets": True,
                                     "distance_between": 5}
        if "junctions" not in config["positioning"]:
            config["positioning"]["junctions"] = {"straight": True, "left": True, "right": True,
                                                  "has_traffic_lights": True}
        if "straight" not in config["positioning"]["junctions"]:
            config["positioning"]["junctions"]["straight"] = True
        if "left" not in config["positioning"]["junctions"]:
            config["positioning"]["junctions"]["left"] = True
        if "right" not in config["positioning"]["junctions"]:
            config["positioning"]["junctions"]["right"] = True
        if "has_traffic_lights" not in config["positioning"]["junctions"]:
            config["positioning"]["junctions"]["has_traffic_lights"] = True
        if "streets" not in config["positioning"]:
            config["positioning"]["streets"] = True
        if not config["positioning"]["streets"] and \
            not config["positioning"]["junctions"]["straight"] and \
            not config["positioning"]["junctions"]["left"] and \
            not config["positioning"]["junctions"]["right"]:
            raise Exception(
                "Actor generators optional properties 'streets' and 'junctions.<direction>' cannot all be 'False'")
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
        if pos_config["junctions"]["has_traffic_lights"] == "Only":
            junctions_in_town = [junction for junction in waypoints_in_town["junctions"].values()
                                 if "traffic_lights" in junction]
        elif not pos_config["junctions"]["has_traffic_lights"]:
            junctions_in_town = [junction for junction in waypoints_in_town["junctions"].values()
                                 if "traffic_lights" not in junction]
        else:
            junctions_in_town = waypoints_in_town["junctions"].values()

        if len(junctions_in_town) == 0:
            raise Exception(f"The requested junctions' traffic light configuration could not be "
                            f"fulfilled for map <{town_name}>! Please exclude it in the "
                            f"'map_blacklist' for this scenario!")

        if pos_config["junctions"]["straight"]:
            allowed_waypoints += [waypoints[0] for junction in junctions_in_town
                                  for waypoints in junction["waypoints_with_straight_turn"]]
        if pos_config["junctions"]["left"]:
            allowed_waypoints += [waypoints[0] for junction in junctions_in_town
                                  for waypoints in junction["waypoints_with_left_turn"]]
        if pos_config["junctions"]["right"]:
            allowed_waypoints += [waypoints[0] for junction in junctions_in_town
                                  for waypoints in junction["waypoints_with_right_turn"]]

        if len(allowed_waypoints) == 0:
            raise Exception(f"The requested junctions' configuration could not be "
                            f"fulfilled for map <{town_name}>! Please exclude it in the "
                            f"'map_blacklist' for this scenario!")

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
