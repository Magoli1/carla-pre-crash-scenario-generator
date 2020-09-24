import copy
import time
import carla
from collections import defaultdict


def is_full_qualified_map_name(name):
    """Checks whether a map-name is fully qualified

    :param name: Generator configuration entity
    :type name: str
    :returns: The result of the check
    :rtype: bool
    """
    splitted_name = name.rsplit('/')
    return len(splitted_name) > 1


def get_duplicates(sequence):
    """Get all duplicates of a list

    :param sequence: Generator configuration entity
    :type sequence: dict
    :returns: The duplicates
    :rtype: list
    """
    seen = set()
    seen_add = seen.add
    seen_twice = set(x for x in sequence if x in seen or seen_add(x))
    return list(seen_twice)


def get_simple_map_name(full_qualified_name):
    """Extracts the simple name given a fully qualified map name

    :param full_qualified_name: The fully qualified map name
    :type full_qualified_name: str
    :returns: The simple name
    :rtype: str
    """
    return full_qualified_name.rsplit('/')[-1]


def get_junction_waypoints(waypoints):
    """Filters the waypoints for the ones on a junction

    :param waypoints: A list of unfiltered waypoints
    :type waypoints: list
    :returns: A dict containing all junctions in the map and their respective waypoints
    :rtype: dict
    """
    # Internal blacklist only
    junctions_blacklist = []

    d = defaultdict(lambda: defaultdict(list))
    junction_waypoints = [(waypoint.get_junction().id, waypoint.get_junction(), waypoint)
                          for waypoint in waypoints
                          if waypoint.is_junction and
                          waypoint.get_junction().id not in junctions_blacklist]
    for k, obj, v in junction_waypoints:
        d[k]["object"] = obj
        d[k]["waypoints_in_junction"].append(v)

    return dict(d)


def get_street_waypoints(waypoints, min_dist_before_junction=50):
    """Filters the waypoints for the ones on a street

    :param waypoints: A list of unfiltered waypoints
    :type waypoints: list
    :param min_dist_before_junction: Distance before a junction
    :type min_dist_before_junction: int
    :returns: Waypoints that lay on a street
    :rtype: list
    """
    return [waypoint for waypoint in waypoints if
            not waypoint.is_junction and
            len(waypoint.next_until_lane_end(1)) > min_dist_before_junction]


def add_traffic_lights_at_junction(carla_client, current_map, map_name, junctions_per_map):
    """Extends the junctions dict by adding the information for the traffic lights at the
    respective junctions

    :param carla_client: Carla client reference
    :type carla_client: object
    :param current_map: Currently loaded map
    :type current_map: object
    :param map_name: Name of the currently loaded map
    :type map_name: String
    :param junctions_per_map: A dict containing all the junctions in the currently loaded map
    :type junctions_per_map: dict
    :returns: Extended junctions dict
    :rtype: dict
    """
    for tl in carla_client.get_world().get_actors().filter('traffic.traffic_light*'):
        point = current_map.get_waypoint(tl.get_location(), project_to_road=True,
                                         lane_type=carla.LaneType.Driving)
        tries = 0
        switch = False
        virgin = True
        threshold = 11
        start_point = point
        try:
            while not point.is_junction:
                # TODO Config EU/US map
                # Problem maps: Town3, Town4, Town5, Town6, Town7, Town10HD
                if map_name in ['Town01, Town02']:
                    point = point.next(1.0)[0]
                else:
                    if tries > threshold and virgin:
                        switch = True
                        virgin = False
                        tries = 0
                        point = start_point
                    elif tries > threshold and not virgin:
                        print("Junction not found in set threshold.")
                        continue

                    if switch and not virgin:
                        point = point.next(1.0)[0]
                        tries += 1
                    else:
                        try:
                            point = point.previous(1.0)[0]
                            tries += 1
                        except IndexError:
                            tries = threshold + 1
        except IndexError:
            print("Junction not found because lane ended earlier.")
            continue

        junction = point.get_junction()
        junctions_per_map[junction.id]["traffic_lights"].append(tl)

    return junctions_per_map


def add_junction_directions(junctions_per_map):
    """ Extends the junctions dict by adding to each junction the information for the turns allowed
    at each lane and their respective direction

    :param junctions_per_map: A dict containing all the junctions in the currently loaded map
    :type junctions_per_map: dict
    :returns: Extended junctions dict
    :rtype: dict
    """
    for junction_id, junction in junctions_per_map.items():
        junction_waypoints = junction["object"].get_waypoints(carla.LaneType.Driving)
        already_seen_waypoints = []
        for lane_id, lane in enumerate(junction_waypoints):
            for waypoint in lane:
                # Check if waypoint is an end-waypoint and map it back to the beginning of the
                # connecting road
                if waypoint.next(10.0)[0].road_id != waypoint.road_id:
                    while waypoint.previous(0.5)[0].road_id == waypoint.road_id:
                        waypoint = waypoint.previous(0.5)[0]
                start_waypoint = waypoint

                # Check if start-waypoint is part of an already tracked connecting road (road + lane)
                if [start_waypoint.road_id, start_waypoint.lane_id] in already_seen_waypoints:
                    continue
                else:
                    already_seen_waypoints.append([start_waypoint.road_id, start_waypoint.lane_id])

                # Determine incoming road
                waypoint_incoming_road = start_waypoint
                connecting_road_id = start_waypoint.road_id
                while waypoint_incoming_road.road_id == connecting_road_id:
                    waypoint_incoming_road = waypoint_incoming_road.previous(0.5)[0]

                # Determine end-waypoint of the connecting road
                end_waypoint = start_waypoint
                while end_waypoint.next(0.5)[0].road_id == end_waypoint.road_id:
                    end_waypoint = end_waypoint.next(0.5)[0]

                # Determine outgoing road
                waypoint_outgoing_road = end_waypoint.next(0.5)[0]

                # Compute position of end-waypoint relative to start-waypoint,
                # to determine the turn's direction
                threshold = 35
                n = end_waypoint.transform.rotation.yaw
                n = n % 360.0
                c = start_waypoint.transform.rotation.yaw
                c = c % 360.0
                diff_angle = (n - c) % 180.0
                if diff_angle < threshold or diff_angle > (180 - threshold):
                    # STRAIGHT
                    junctions_per_map[junction_id]["waypoints_with_straight_turn"].append(
                        (waypoint_incoming_road,
                         start_waypoint,
                         waypoint_outgoing_road))
                elif diff_angle > 90.0:
                    # LEFT
                    junctions_per_map[junction_id]["waypoints_with_left_turn"].append(
                        (waypoint_incoming_road,
                         start_waypoint,
                         waypoint_outgoing_road))
                else:
                    # RIGHT
                    junctions_per_map[junction_id]["waypoints_with_right_turn"].append(
                        (waypoint_incoming_road,
                         start_waypoint,
                         waypoint_outgoing_road))

    return junctions_per_map


def change_map(carla_client, map_name, number_tries=10, timeout=2):
    """Timeout-aware function to change the carla map

    It is possible that the world does not connect in the timeout of 10x 2sec, so for "slower"
    computers, this function implements a longer timeout on top of the builtin mechanism.

    :param carla_client: Carla client reference
    :type carla_client: object
    :param map_name: Name of the map to change to, either fully qualified or simple name
    :type map_name: str
    :param number_tries: Number of retries when connecting to the new map
    :type number_tries: int
    :param timeout: Timeout in seconds to wait before each retry
    :type timeout: int
    """
    try:
        carla_client.load_world(map_name)
    except:
        pass
    for idx in range(number_tries):
        # this fails if its currently changing as it cant connect in before timeout
        try:
            carla_client.get_world().get_map()
        except:
            print(f'Attempt #{idx + 1} to get new map...')
        else:
            print(f'New map loaded at attempt #{idx + 1}')
            break
        if idx == (number_tries - 1):
            raise Exception(
                "Could not change world in time. Please raise the timeout of the world loading")
        time.sleep(timeout)


def extend_scenarios(tree, number_copies, step_idx):
    """Duplicates the scenario contained in the passed xml-tree the given number of times

    The result is contained in the passed xml-tree by reference.

    :param tree: The xml tree with scenarios to duplicate
    :type tree: object
    :param number_copies: NUmber of copies to make of each scenario entry
    :type number_copies: int
    :param step_idx: Index of the step in the pipeline. Used for better naming of the scenarios
    :type step_idx: int
    """
    if number_copies <= 0:
        return
    root = tree.getroot()
    children = root.getchildren()
    for idx, scenario in enumerate(children):
        for inner_idx in range(number_copies):
            new_scenario = copy.deepcopy(scenario)
            # TODO Naming could be enhanced
            new_scenario.set("name", f'{new_scenario.get("name")}-{step_idx}-{inner_idx}')
            root.insert(idx + 1 + inner_idx + idx * number_copies, new_scenario)
