from core.xml.initializer import initialize_xml_tree
from core.xml.file_writer import write_xml

from core.plugin.loader import get_plugin_classes_in_configured_order
from core.configuration.loader import get_config

import carla
import argparse


def main():
    generator_config = get_config()
    args = get_args()
    client = carla.Client(args.host, args.port)
    client.set_timeout(args.timeout)

    tree = initialize_xml_tree()
    start_pipeline(client, generator_config, tree)
    write_xml(tree)


def start_pipeline(carla_client, generator_config, tree):
    classes = get_plugin_classes_in_configured_order(generator_config["pipeline"])
    for idx, Class in enumerate(classes):
        step_config = generator_config["pipeline"][idx]
        if not isinstance(step_config, dict):
            step_config = dict()
        else:
            step_config = list(step_config.values())[0]
        instance = Class(carla_client, step_config)
        instance.generate(tree)


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
