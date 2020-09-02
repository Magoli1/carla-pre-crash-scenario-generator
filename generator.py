from core.xml.initializer import initialize_xml_tree
from core.xml.file_writer import write_xml

from core.plugin.loader import get_plugin_classes_in_configured_order
from core.configuration.loader import get_config
from core.configuration.utils import extract_pipeline_name, extract_pipeline_config
from core.data.provider import DataProvider

import carla
import argparse


def main():
    generator_config = get_config()
    args = get_args()
    client = carla.Client(args.host, args.port)
    client.set_timeout(args.timeout)

    data_provider = DataProvider(client)
    start_pipeline(client, generator_config, data_provider)


def start_pipeline(carla_client, generator_config, data_provider):
    pipelines = generator_config["pipelines"]
    if generator_config["dataprovider"]["preload"]:
        print("### START preloading data START ###")
        data_provider.preload()
        print("### END preloading data END ###")
    print("### Running pipelines... ###")
    for pipeline in pipelines:
        pipeline_name = extract_pipeline_name(pipeline)
        print(f'## START pipeline "{pipeline_name}" START ##')
        tree = initialize_xml_tree()
        pipeline_config = extract_pipeline_config(pipeline)
        classes = get_plugin_classes_in_configured_order(pipeline_config["steps"])
        for idx, Class in enumerate(classes):
            print(f'# START pipeline step #{idx} {Class.__name__} START #')
            step_config = pipeline_config["steps"][idx]
            if not isinstance(step_config, dict):
                step_config = dict()
            else:
                step_config = list(step_config.values())[0]
            instance = Class(carla_client, step_config, data_provider, idx)
            instance.generate(tree)
            print(f'# END pipeline step #{idx} {Class.__name__} END #')
        write_xml(tree, filename=pipeline_name)
        print(f'## END pipeline "{pipeline_name}" END ##')


def get_args():
    argparser = argparse.ArgumentParser(description=__doc__)
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
        default=10.0,
        type=float,
        help='Timeout of the carla client (default: 10.0)')
    return argparser.parse_args()


if __name__ == "__main__":
    print("#### Pre Crash Scenrio Generator ####")
    main()
    print("#### Generating data done! *Happy Face* ####")
