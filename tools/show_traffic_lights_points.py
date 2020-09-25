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


def main():
    try:

        client = carla.Client('localhost', 2000)
        world = client.get_world()
        client.reload_world()
        map = world.get_map()

        # Get all traffic light points
        counter = 0
        for tl in world.get_actors().filter('traffic.traffic_light*'):
            point = map.get_waypoint(tl.get_location(), project_to_road=True,
                                     lane_type=carla.LaneType.Driving)
            if not point.is_junction:
                id = 0
                tries = 0
                switch = False
                virgin = True
                threshold = 15
                start_point = point
                try:
                    while not point.is_junction:
                        if map.name in ['Town01, Town02']:
                            point = point.next(1.0)[0]
                        else:
                            if tries > threshold and virgin:
                                switch = True
                                virgin = False
                                tries = 0
                                point = start_point
                            elif tries > threshold and not virgin:
                                raise ValueError("Traffic light not found in set threshold.")

                            if switch and not virgin:
                                point = point.next(1.0)[0]
                                tries += 1
                            else:
                                try:
                                    point = point.previous(1.0)[0]
                                    tries += 1
                                except IndexError:
                                    tries = threshold + 1

                        if point.is_junction:
                            world.debug.draw_string(point.transform.location, f'J_{id}',
                                                    draw_shadow=False,
                                                    color=carla.Color(r=255, g=0, b=0),
                                                    life_time=9000.0,
                                                    persistent_lines=True)
                        else:
                            world.debug.draw_string(point.transform.location, f'N_{id}',
                                                    draw_shadow=False,
                                                    color=carla.Color(r=255, g=0, b=0),
                                                    life_time=9000.0,
                                                    persistent_lines=True)
                        id += 1
                except IndexError:
                    print("NOT FOUND!")
                    world.debug.draw_string(start_point.transform.location, f'UNKNOWN',
                                            draw_shadow=False,
                                            color=carla.Color(r=0, g=0, b=0),
                                            life_time=9000.0,
                                            persistent_lines=True)
            else:
                print("Good")
                world.debug.draw_string(point.transform.location, 'J', draw_shadow=False,
                                        color=carla.Color(r=0, g=255, b=0), life_time=9000.0,
                                        persistent_lines=True)

                counter += 1
            print("#" * 10)
        print(f"Detected junction traffic lights: {counter}")

    finally:
        print('Done.')


if __name__ == '__main__':
    main()
