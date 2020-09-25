from xml.etree.ElementTree import SubElement

from core.helpers.utils import extend_scenarios, RoadDirection, get_direction_between_points

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

        if "relative_to_ego" not in config["positioning"]["junctions"]:
            config["positioning"]["junctions"]["relative_to_ego"] \
                = {"straight": True, "left": True, "right": True}
        if "straight" not in config["positioning"]["junctions"]["relative_to_ego"]:
            config["positioning"]["junctions"]["relative_to_ego"]["straight"] = True
        if "left" not in config["positioning"]["junctions"]["relative_to_ego"]:
            config["positioning"]["junctions"]["relative_to_ego"]["left"] = True
        if "right" not in config["positioning"]["junctions"]["relative_to_ego"]:
            config["positioning"]["junctions"]["relative_to_ego"]["right"] = True

        if "streets" not in config["positioning"]:
            config["positioning"]["streets"] = True

        if "has_traffic_lights" not in config["positioning"]["junctions"]:
            config["positioning"]["junctions"]["has_traffic_lights"] = True

        if not config["positioning"]["streets"] and \
            not config["positioning"]["junctions"]["straight"] and \
            not config["positioning"]["junctions"]["left"] and \
            not config["positioning"]["junctions"]["right"]:
            raise Exception(
                "Actor generators optional properties 'streets' and 'junctions.<direction>' cannot all be 'False'")

        if (config["tag"] == "other_actor"
            and not all(switch is False for switch
                        in config["positioning"]["junctions"]["relative_to_ego"].values())
            and (not config["positioning"]["junctions"]["straight"] and
                 not config["positioning"]["junctions"]["left"] and
                 not config["positioning"]["junctions"]["right"])):
            raise Exception(
                "Actor generators optional properties of 'relative_to_ego' "
                "cannot be 'True' if all directions in 'junctions' are 'False'"
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
                print(f"One Scenario was removed, because there is no "
                      f"allowed waypoint for {self.config['tag']}")
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
                if pos_config["streets"]:
                    return [(waypoint, None, None, None) for waypoint in waypoints_in_town["streets"]]
                else:
                    return []

            allowed_directions = []
            if pos_config["junctions"]["relative_to_ego"]["straight"]:
                allowed_directions.append(RoadDirection.FRONT)
            if pos_config["junctions"]["relative_to_ego"]["left"]:
                allowed_directions.append(RoadDirection.LEFT)
            if pos_config["junctions"]["relative_to_ego"]["right"]:
                allowed_directions.append(RoadDirection.RIGHT)

            possible_waypoints = []
            if pos_config["junctions"]["straight"]:
                possible_waypoints += [(*waypoints, junction_id) for waypoints
                                      in waypoints_in_town["junctions"][junction_id]["waypoints_with_straight_turn"]]
            if pos_config["junctions"]["left"]:
                possible_waypoints += [(*waypoints, junction_id) for waypoints
                                      in waypoints_in_town["junctions"][junction_id]["waypoints_with_left_turn"]]
            if pos_config["junctions"]["right"]:
                possible_waypoints += [(*waypoints, junction_id) for waypoints
                                      in waypoints_in_town["junctions"][junction_id]["waypoints_with_right_turn"]]

            for waypoints in possible_waypoints:
                if get_direction_between_points(
                        start_point_yaw,
                        waypoints[1].transform.rotation.yaw) in allowed_directions:
                    allowed_waypoints.append((*waypoints, junction_id))

        else:
            if pos_config["junctions"]["has_traffic_lights"] == "Only":
                junctions_in_town = [junction for junction in waypoints_in_town["junctions"].values()
                                    if "traffic_lights" in junction]
            elif not pos_config["junctions"]["has_traffic_lights"]:
                junctions_in_town = [junction for junction in waypoints_in_town["junctions"].values()
                                    if "traffic_lights" not in junction]
            else:
                junctions_in_town = waypoints_in_town["junctions"].values()

            if not pos_config["streets"] and len(junctions_in_town) == 0:
                raise Exception(f"The requested junctions' traffic light configuration could not be "
                                f"fulfilled for map <{town_name}>! Please exclude it in the "
                                f"'map_blacklist' for this scenario!")

            if pos_config["junctions"]["straight"]:
                allowed_waypoints += [(*waypoints, junction["object"].id) for junction in junctions_in_town
                                    for waypoints in junction["waypoints_with_straight_turn"]]
            if pos_config["junctions"]["left"]:
                allowed_waypoints += [(*waypoints, junction["object"].id) for junction in junctions_in_town
                                    for waypoints in junction["waypoints_with_left_turn"]]
            if pos_config["junctions"]["right"]:
                allowed_waypoints += [(*waypoints, junction["object"].id) for junction in junctions_in_town
                                    for waypoints in junction["waypoints_with_right_turn"]]

            if not pos_config["streets"] and len(allowed_waypoints) == 0:
                raise Exception(f"The requested junctions' configuration could not be "
                                f"fulfilled for map <{town_name}>! Please exclude it in the "
                                f"'map_blacklist' for this scenario!")

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
