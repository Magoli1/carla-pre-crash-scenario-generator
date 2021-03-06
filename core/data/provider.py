import carla
from tqdm import tqdm

from core.helpers.utils import get_simple_map_name, change_map, get_junction_waypoints, \
    get_street_waypoints, add_traffic_lights_at_junction, add_junction_directions
from core.logger.logger import logger


def get_waypoints_for_all_maps(carla_client, distance=5):
    """Gets all waypoints for all maps by loading the individual maps

    :param carla_client: Carla client reference
    :type carla_client: object
    :param distance: Distance in which to find waypoints
    :type distance: int
    :returns: All waypoints on all maps that could be found
    :rtype: list
    """
    available_map_names = carla_client.get_available_maps()
    waypoints_per_map = dict()

    with tqdm(available_map_names, leave=False) as t:
        for map_name in t:
            map_name = get_simple_map_name(map_name)
            t.set_description(f'DataProvider.LoadWayPoints: Changing map to {map_name}')
            change_map(carla_client, map_name)
            t.set_description(
                f'DataProvider.LoadWayPoints: Generating waypoints for map {map_name}')
            current_map = carla_client.get_world().get_map()
            waypoints = current_map.generate_waypoints(distance)
            waypoints_per_map[map_name] = dict()
            waypoints_per_map[map_name]["junctions"] = get_junction_waypoints(waypoints, map_name)
            waypoints_per_map[map_name]["streets"] = get_street_waypoints(waypoints)
            waypoints_per_map[map_name]["junctions"] = add_traffic_lights_at_junction(carla_client,
                                                                                      current_map,
                                                                                      map_name,
                                                                                      waypoints_per_map[
                                                                                          map_name][
                                                                                          "junctions"])
            waypoints_per_map[map_name]["junctions"] = add_junction_directions(
                waypoints_per_map[map_name]["junctions"])
        t.set_description(f'DataProvider.LoadWayPoints: Loaded all maps')
    return waypoints_per_map


class DataProvider:
    """This class creates a data caching layer for long running data fetch tasks
    """

    def __init__(self, carla_client):
        """Constructor of DataProvider class

        :param carla_client: Carla client reference
        :type carla_client: object
        """
        self.client = carla_client
        self.waypoints_per_map = None
        self.available_maps = None
        self.preloaded = False

    def preload(self):
        """Preloads all registered long running data tasks for access on the fast cache layer
        """
        if self.preloaded:
            logger.error("DataProvider: Preloading of data is already done. Dont call it twice")
            raise SystemExit(0)
        self.get_waypoints_per_map()
        self.get_available_maps_simple_name()
        self.preloaded = True

    def get_waypoints_per_map(self):
        """Gets all waypoints for all maps that can be found

        :returns: All waypoints for all maps that could be found
        :rtype: list
        """
        if self.waypoints_per_map is None:
            logger.debug("DataProvider.LoadWayPoints: Starting to load waypoints for all maps...")
            self.waypoints_per_map = get_waypoints_for_all_maps(self.client)
            logger.debug("DataProvider:LoadWayPoints Waypoints loaded for all maps successfully")
        return self.waypoints_per_map

    def get_available_maps_simple_name(self):
        """Get the simple names of all available maps eg. Town01, Town02

        :returns: All simple names of all available names
        :rtype: list
        """
        if self.available_maps is None:
            logger.debug("DataProvider.LoadSimpleMapNames: Starting to load simple map names...")
            available_maps = self.client.get_available_maps()
            self.available_maps = [get_simple_map_name(map_name) for map_name in available_maps]
            logger.debug("DataProvider.LoadSimpleMapNames: Simple map names loaded successfully")
        return self.available_maps
