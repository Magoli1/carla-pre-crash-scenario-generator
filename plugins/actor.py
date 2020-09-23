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
        if "junctions" not in config["positioning"] or config["positioning"]["junctions"] is True:
            config["positioning"]["junctions"] = {"straight": True, "left": True, "right": True}
        elif config["positioning"]["junctions"] is False:
            config["positioning"]["junctions"] = {"straight": False, "left": False, "right": False}
        if "straight" not in config["positioning"]["junctions"]:
            config["positioning"]["junctions"]["straight"] = True
        if "left" not in config["positioning"]["junctions"]:
            config["positioning"]["junctions"]["left"] = True
        if "right" not in config["positioning"]["junctions"]:
            config["positioning"]["junctions"]["right"] = True

        if config["tag"] != "other_actor" and "streets" not in config["positioning"]:
            config["positioning"]["streets"] = True

        if "relative_to_ego" not in config["positioning"]["junctions"]:
            config["positioning"]["junctions"]["relative_to_ego"] \
                = {"straight": True, "left": True, "right": True}
        if "straight" not in config["positioning"]["junctions"]["relative_to_ego"]:
            config["positioning"]["junctions"]["relative_to_ego"]["straight"] = True
        if "left" not in config["positioning"]["junctions"]["relative_to_ego"]:
            config["positioning"]["junctions"]["relative_to_ego"]["left"] = True
        if "right" not in config["positioning"]["junctions"]["relative_to_ego"]:
            config["positioning"]["junctions"]["relative_to_ego"]["right"] = True

        if (config["tag"] == "other_actor"
                and all(switch is False for switch in config["positioning"]["junctions"]["relative_to_ego"].values())):
            raise Exception(
                "Actor generators optional properties in "
                "'relative_to_ego' cannot all be 'False' for 'other_actor'"
            )
        if config["tag"] == "other_actor" and config["positioning"].get("streets") is True:
            raise Exception(
                "Actor generators optional property 'streets' "
                "cannot be 'True' for 'other_actor'"
            )
        if (not config["positioning"]["streets"]
                and all(switch is False for switch in config["positioning"]["junctions"].values()
                        if isinstance(switch, bool))):
            raise Exception(
                "Actor generators optional properties 'streets' "
                "and all directions in 'junctions' cannot both be 'False'"
            )

        self.config = config
        self.data_provider = data_provider
        self.step_idx = step_idx

    def generate(self, tree):
        extend_scenarios(tree, self.config["per_scenario"] - 1, self.step_idx)
        for scenario in tree.getroot().getchildren():
            actor = SubElement(scenario, self.config["tag"])
            attributes = {}
            if self.config["tag"] == "other_actor":
                relative_to_ego = not all(switch is False for switch in
                                          self.config["positioning"]["junctions"]["relative_to_ego"].values())
                ego_vehicle = scenario.find("ego_vehicle")
                junction_id = None
                start_point_yaw = None
                if ego_vehicle is not None:
                    junction_id = ego_vehicle.get("junction_id")
                    start_point_yaw = ego_vehicle.get("start_point_yaw")
                if junction_id is not None:
                    junction_id = int(junction_id)
                if start_point_yaw is not None:
                    start_point_yaw = float(start_point_yaw)
                allowed_waypoints = self.get_allowed_waypoints_in_town(scenario.get("town"),
                                                                       relative_to_ego,
                                                                       junction_id,
                                                                       start_point_yaw)
            else:
                allowed_waypoints = self.get_allowed_waypoints_in_town(scenario.get("town"))
            if not allowed_waypoints:
                tree.getroot().remove(scenario)
                continue
            waypoint = random.choice(allowed_waypoints)
            attributes["waypoint"] = waypoint[0]
            if waypoint[3]:
                attributes["junction_id"] = waypoint[3]
            if waypoint[1]:
                attributes["start_point_yaw"] = waypoint[1]
            attributes["actor_model"] = random.choice(self.actor_models)
            self.decorate_actor(actor, **attributes)

    def get_allowed_waypoints_in_town(self, town_name: str, relative_to_ego: bool = False,
                                      junction_id: int = None, start_point_yaw: float = None):
        pos_config = self.config["positioning"]
        waypoints_in_town = self.data_provider.get_waypoints_per_map()[town_name]
        allowed_waypoints = []

        if relative_to_ego:
            if not junction_id or not start_point_yaw:
                return []

        else:
            if pos_config["junctions"]["straight"]:
                allowed_waypoints += [(*waypoints, junction["object"].id) for junction in waypoints_in_town["junctions"].values()
                                    for waypoints in junction["waypoints_with_straight_turn"]]
            if pos_config["junctions"]["left"]:
                allowed_waypoints += [(*waypoints, junction["object"].id) for junction in waypoints_in_town["junctions"].values()
                                    for waypoints in junction["waypoints_with_left_turn"]]
            if pos_config["junctions"]["right"]:
                allowed_waypoints += [(*waypoints, junction["object"].id) for junction in waypoints_in_town["junctions"].values()
                                    for waypoints in junction["waypoints_with_right_turn"]]
            if pos_config["streets"]:
                allowed_waypoints += [(waypoint, None, None, None)
                                      for waypoint in waypoints_in_town["streets"]]

        return allowed_waypoints

    def decorate_actor(self, actor, **kwargs):
        if "waypoint" in kwargs:
            actor.set("x", str(round(kwargs["waypoint"].transform.location.x, 2)))
            actor.set("y", str(round(kwargs["waypoint"].transform.location.y, 2)))
            actor.set("z", str(round(kwargs["waypoint"].transform.location.z, 2)))
            actor.set("yaw", str(round(kwargs["waypoint"].transform.rotation.yaw, 2)))

        if "actor_model" in kwargs:
            actor.set("model", kwargs["actor_model"])

        if "junction_id" in kwargs:
            actor.set("junction_id", str(kwargs["junction_id"]))

        if "start_point_yaw" in kwargs:
            actor.set("start_point_yaw", str(
                round(kwargs["start_point_yaw"].transform.rotation.yaw, 2)))
