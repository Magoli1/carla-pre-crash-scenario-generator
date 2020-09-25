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


def main():
    try:

        dist = 5.0  # Distance between all waypoints generated

        client = carla.Client('localhost', 2000)
        world = client.get_world()
        client.reload_world()
        map = world.get_map()

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
                    # STRAIGHT
                    world.debug.draw_string(wp_end.transform.location,
                                            f'E Straight - {wp_end.road_id}',
                                            draw_shadow=False,
                                            color=carla.Color(r=r, g=g, b=b), life_time=999.0,
                                            persistent_lines=True)
                elif diff_angle > 90.0:
                    # LEFT
                    world.debug.draw_string(wp_end.transform.location,
                                            f'E Left - {wp_end.road_id}',
                                            draw_shadow=False,
                                            color=carla.Color(r=r, g=g, b=b), life_time=999.0,
                                            persistent_lines=True)
                else:
                    # RIGHT
                    world.debug.draw_string(wp_end.transform.location,
                                            f'E Right - {wp_end.road_id}',
                                            draw_shadow=False,
                                            color=carla.Color(r=r, g=g, b=b), life_time=999.0,
                                            persistent_lines=True)

    finally:
        print('Done.')


if __name__ == '__main__':
    main()
