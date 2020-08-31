import time
import copy


def is_full_qualified_map_name(name):
    splitted_name = name.rsplit('/')
    return len(splitted_name) > 1


def get_duplicates(sequence):
    seen = set()
    seen_add = seen.add
    seen_twice = set(x for x in sequence if x in seen or seen_add(x))
    return list(seen_twice)


def get_simple_map_name(full_qualified_name):
    return full_qualified_name.rsplit('/')[-1]


def get_junction_waypoints(waypoints):
    return [waypoint for waypoint in waypoints if waypoint.is_junction]


def get_street_waypoints(waypoints):
    return [waypoint for waypoint in waypoints if not waypoint.is_junction]


def change_map(carla_client, map_name, number_tries=10, timeout=2):
    # its possible that the world does not connect in the timeout of 10x 2sec
    # -> needs manual check
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
