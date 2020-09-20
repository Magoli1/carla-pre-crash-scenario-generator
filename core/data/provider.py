import carla
from core.helpers.utils import get_simple_map_name, change_map, get_junction_waypoints, \
    get_street_waypoints, get_traffic_lights_at_junction, get_junction_directions


def get_waypoints_for_all_maps(carla_client, distance=5):
    available_map_names = carla_client.get_available_maps()
    waypoints_per_map = dict()
    for map_name in available_map_names:
        map_name = get_simple_map_name(map_name)
        print(f'DataProvider.LoadWayPoints: Changing map to {map_name}...')
        change_map(carla_client, map_name)
        print(f'DataProvider.LoadWayPoints: Generating waypoints for map {map_name}...')
        current_map = carla_client.get_world().get_map()
        waypoints = current_map.generate_waypoints(distance)
        waypoints_per_map[map_name] = dict()
        waypoints_per_map[map_name]["junctions"] = get_junction_waypoints(waypoints)
        waypoints_per_map[map_name]["streets"] = get_street_waypoints(waypoints)
        waypoints_per_map[map_name]["junctions"] = get_traffic_lights_at_junction(carla_client,
                                                                                  current_map,
                                                                                  map_name,
                                                                                  waypoints_per_map[map_name]["junctions"])
        waypoints_per_map[map_name]["junctions"] = get_junction_directions(waypoints_per_map[map_name]["junctions"])

    return waypoints_per_map


class DataProvider:
    def __init__(self, carla_client):
        self.client = carla_client
        self.waypoints_per_map = None
        self.available_maps = None
        self.preloaded = False
        pass

    def preload(self):
        if self.preloaded:
            raise Exception("DataProvider: Preloading of data is already done. Dont call it twice")
        self.get_waypoints_per_map()
        self.get_available_maps_simple_name()
        self.preloaded = True

    def get_waypoints_per_map(self):
        if self.waypoints_per_map is None:
            print("DataProvider.LoadWayPoints: Starting to load waypoints for all maps...")
            self.waypoints_per_map = get_waypoints_for_all_maps(self.client)
            print("DataProvider:LoadWayPoints Waypoints loaded for all maps successfully")
        return self.waypoints_per_map

    def get_available_maps_simple_name(self):
        if self.available_maps is None:
            print("DataProvider.LoadSimpleMapNames: Starting to load simple map names...")
            available_maps = self.client.get_available_maps()
            self.available_maps = [get_simple_map_name(map_name) for map_name in available_maps]
            print("DataProvider.LoadSimpleMapNames: Simple map names loaded successfully")
        return self.available_maps
