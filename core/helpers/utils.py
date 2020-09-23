import copy
import time


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
    :returns: Waypoints that lay on a junction
    :rtype: list
    """
    return [waypoint for waypoint in waypoints if waypoint.is_junction]


def get_street_waypoints(waypoints, min_dist_before_junction=80, min_dist_after_junction=10):
    """Filters the waypoints for the ones on a street

    :param waypoints: A list of unfiltered waypoints
    :type waypoints: list
    :param min_dist_before_junction: Distance before a junction
    :type min_dist_before_junction: int
    :param min_dist_after_junction: Distance after a junction
    :type min_dist_after_junction: int
    :returns: Waypoints that lay on a street
    :rtype: list
    """
    # Get rid of waypoints too close to a junction (in front)
    waypoints = [waypoint for waypoint in waypoints if
                 not waypoint.is_junction and
                 len(waypoint.next_until_lane_end(1)) > min_dist_before_junction]

    # Get rid of waypoints too close to a junction (in back)
    valid_waypoints = []
    for waypoint in waypoints:
        prev_waypoints_in_junction = [prev_waypoint for prev_waypoint in
                                      waypoint.previous(min_dist_after_junction) if
                                      prev_waypoint.is_junction]
        if len(prev_waypoints_in_junction) == 0:
            valid_waypoints.append(waypoint)

    return valid_waypoints


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
