import glob
import os
import sys

try:
    sys.path.append(glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

import carla

import random
import time


def main():

    try:
        
        dist = 5.0 # Distance between all waypoints generated
        visualize = True # Switch for visualizing waypoints
        
        client = carla.Client('localhost', 2000)
        world = client.get_world() 
        map = world.get_map()

        # Generate all waypoints with given distance
        waypoint_list = map.generate_waypoints(dist)
        print("Number of Waypoints with distance of {}: {}". format(dist, len(waypoint_list)))

        waypoints_belonging_2_junction = []
        for waypoint in waypoint_list:
            # Not pretty but only way I found fo checking if waypoint belongs to a junction
            if waypoint.get_junction() is not None:
                waypoints_belonging_2_junction.append(waypoint)

        print("Number of waypoints belonging to junction {}". format(len(waypoints_belonging_2_junction)))
        
        if visualize == True:
            for w in waypoints_belonging_2_junction:
                world.debug.draw_string(w.transform.location, 'O', draw_shadow=False,
                                        color=carla.Color(r=255, g=0, b=0), life_time=10.0,
                                        persistent_lines=True)


        # Get all spawn points
        spawn_points = map.get_spawn_points()
        for spawn_point in spawn_points:
            world.debug.draw_string(spawn_point.location, 'X', draw_shadow=False,
                        color=carla.Color(r=0, g=0, b=255), life_time=10.0,
                        persistent_lines=True)

    finally:
        print('Done.')


if __name__ == '__main__':
    main()
