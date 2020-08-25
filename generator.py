

from core.xml.initializer import initialize_xml_tree
from core.xml.file_writer import write_xml

from core.plugin.loader import get_plugin_classes

#import carla
import argparse


def main():
    classes = get_plugin_classes()
    for Class in classes:
        instance = Class("test")
        instance.test()

    args = get_args()
    client = carla.Client(args.host, args.port)
    client.set_timeout(args.timeout)

    tree = initialize_xml_tree()

    write_xml(tree)


def get_args():
    argparser = argparse.ArgumentParser(
        description=__doc__)
    argparser.add_argument(
        '--host',
        metavar='H',
        default='127.0.0.1',
        help='IP of the host server (default: 127.0.0.1)')
    argparser.add_argument(
        '-p', '--port',
        metavar='P',
        default=2000,
        type=int,
        help='TCP port to listen to (default: 2000)')
    argparser.add_argument(
        '-t', '--timeout',
        metavar='t',
        default=5.0,
        type=float,
        help='Timeout of the carla client (default: 5.0)')
    return argparser.parse_args()


if __name__ == "__main__":
    print("#### Pre Crash Scenrio Generator ####")
    main()
