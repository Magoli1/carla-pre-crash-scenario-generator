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

        dist = 5.0  # Distance between all waypoints generated
        visualize = True  # Switch for visualizing waypoints

        client = carla.Client('localhost', 2000)
        world = client.get_world()
        client.reload_world()
        map = world.get_map()
        # file1 = open("map.xml", "w")
        # file1.write(map.to_opendrive())

        # Generate all waypoints with given distance
        waypoint_list = map.generate_waypoints(dist)
        print("Number of Waypoints with distance of {}: {}".format(dist, len(waypoint_list)))

        waypoints_belonging_2_junction = []
        for waypoint in waypoint_list:
            # Not pretty but only way I found fo checking if waypoint belongs to a junction
            if waypoint.get_junction() is not None:
                waypoints_belonging_2_junction.append(waypoint)

        print("Number of waypoints belonging to junction {}".format(
            len(waypoints_belonging_2_junction)))

        if visualize == True:
            for w in waypoints_belonging_2_junction:
                world.debug.draw_string(w.transform.location, 'O', draw_shadow=False,
                                        color=carla.Color(r=255, g=0, b=0), life_time=10.0,
                                        persistent_lines=True)

        # Get all spawn points
        spawn_points = map.get_spawn_points()
        for spawn_point in spawn_points:
            world.debug.draw_string(spawn_point.location, 'X', draw_shadow=False,
                                    color=carla.Color(r=0, g=255, b=0), life_time=999.0,
                                    persistent_lines=True)

        # Get Junction waypoints
        junction_waypoints = waypoints_belonging_2_junction[0].get_junction().get_waypoints(carla.LaneType.Driving)
        already_seen = []
        for l_i, lane in enumerate(junction_waypoints):
            for i, wp in enumerate(lane):
                r = random.randint(0, 255)
                g = random.randint(0, 255)
                b = random.randint(0, 255)
                if wp.next(10.0)[0].road_id != wp.road_id:
                    while wp.previous(0.5)[0].road_id == wp.road_id:
                        wp = wp.previous(0.5)[0]
                wp_start = wp

                if [wp_start.road_id, wp_start.lane_id] in already_seen:
                    continue
                else:
                    already_seen.append([wp_start.road_id, wp_start.lane_id])

                print(f'{i}: {wp_start.road_id}/{wp_start.lane_id}')

                world.debug.draw_string(wp_start.transform.location, f'S - {wp_start.road_id}', draw_shadow=False,
                                        color=carla.Color(r=r, g=g, b=b), life_time=999.0,
                                        persistent_lines=True)
                # for prev_wp in [wp.previous(1.0)[0], wp.previous(5.0)[0], wp.previous(20.0)[0], wp.next(1.0)[0], wp.next(2.0)[0], wp.next(5.0)[0], wp.next(10.0)[0], wp.next(20.0)[0]]:
                #     world.debug.draw_string(prev_wp.transform.location,
                #                             f'{prev_wp.road_id}/{prev_wp.section_id}/{prev_wp.lane_id}',
                #                             draw_shadow=False,
                #                             color=carla.Color(r=r, g=g, b=b), life_time=999.0,
                #                             persistent_lines=True)
                wp_end = wp_start
                while wp_end.next(0.5)[0].road_id == wp_end.road_id:
                    wp_end = wp_end.next(0.5)[0]
                wp_end = wp_end.previous(0.5)[0]


                threshold = 35
                n = wp_end.transform.rotation.yaw
                n = n % 360.0
                c = wp_start.transform.rotation.yaw
                c = c % 360.0
                diff_angle = (n - c) % 180.0
                if diff_angle < threshold or diff_angle > (180 - threshold):
                    # return RoadOption.STRAIGHT
                    world.debug.draw_string(wp_end.transform.location,
                                            f'E Straight - {wp_end.road_id}',
                                            draw_shadow=False,
                                            color=carla.Color(r=r, g=g, b=b), life_time=999.0,
                                            persistent_lines=True)
                elif diff_angle > 90.0:
                    # return RoadOption.LEFT
                    world.debug.draw_string(wp_end.transform.location,
                                            f'E Left - {wp_end.road_id}',
                                            draw_shadow=False,
                                            color=carla.Color(r=r, g=g, b=b), life_time=999.0,
                                            persistent_lines=True)
                else:
                    # return RoadOption.RIGHT
                    world.debug.draw_string(wp_end.transform.location,
                                            f'E Right - {wp_end.road_id}',
                                            draw_shadow=False,
                                            color=carla.Color(r=r, g=g, b=b), life_time=999.0,
                                            persistent_lines=True)

            print('#' * 10)


        # # Get all traffic light points
        # counter = 0
        # for tl in world.get_actors().filter('traffic.traffic_light*'):
        #     point = map.get_waypoint(tl.get_location(), project_to_road=True,
        #                              lane_type=carla.LaneType.Driving)
        #     if not point.is_junction:
        #         id = 0
        #         tries = 0
        #         switch = False
        #         virgin = True
        #         threshold = 15
        #         start_point = point
        #         try:
        #             while not point.is_junction:
        #                 if map.name in ['Town01, Town02']:
        #                     point = point.next(1.0)[0]
        #                 else:
        #                     if tries > threshold and virgin:
        #                         switch = True
        #                         virgin = False
        #                         tries = 0
        #                         point = start_point
        #                     if tries > threshold and not virgin:
        #                         raise ValueError("Traffic light not found in set threshold.")
        #                     if switch and not virgin:
        #                         point = point.next(1.0)[0]
        #                         tries += 1
        #                     else:
        #                         try:
        #                             point = point.previous(1.0)[0]
        #                             tries += 1
        #                         except IndexError:
        #                             tries = threshold + 1
        #
        #                 if point.is_junction:
        #                     world.debug.draw_string(point.transform.location, f'J_{id}',
        #                                             draw_shadow=False,
        #                                             color=carla.Color(r=255, g=0, b=0),
        #                                             life_time=9000.0,
        #                                             persistent_lines=True)
        #                 else:
        #                     world.debug.draw_string(point.transform.location, f'N_{id}',
        #                                             draw_shadow=False,
        #                                             color=carla.Color(r=255, g=0, b=0),
        #                                             life_time=9000.0,
        #                                             persistent_lines=True)
        #                 id += 1
        #         except IndexError:
        #             print("NOT FOUND!")
        #             world.debug.draw_string(start_point.transform.location, f'UNKNOWN',
        #                                     draw_shadow=False,
        #                                     color=carla.Color(r=0, g=0, b=0),
        #                                     life_time=9000.0,
        #                                     persistent_lines=True)
        #     else:
        #         print("Good")
        #         world.debug.draw_string(point.transform.location, 'J', draw_shadow=False,
        #                                 color=carla.Color(r=0, g=255, b=0), life_time=9000.0,
        #                                 persistent_lines=True)
        #
        #         counter += 1
        #     print("#" * 10)
        # print(f"Detected junction traffic lights: {counter}")

    finally:
        print('Done.')


if __name__ == '__main__':
    main()
