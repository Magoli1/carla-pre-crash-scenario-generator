#!/usr/bin/env python3
import carla
import argparse
import logging

from core.xml.initializer import initialize_xml_tree
from core.xml.file_writer import write_xml
from core.plugin.loader import get_plugin_classes_in_configured_order
from core.configuration.loader import get_config
from core.configuration.utils import extract_pipeline_name, extract_pipeline_config
from core.data.provider import DataProvider
from core.logger.logger import logger, set_logging_level, get_plugin_logger


def main():
    """Main function that reads the configuration and starts the pipeline(s)
    """
    args = get_args()
    set_logging_level(args.loglevel)
    logger.info("#### Pre Crash Scenario Generator ####")
    generator_config = get_config(args.config)
    client = carla.Client(args.host, args.port)
    client.set_timeout(args.timeout)

    data_provider = DataProvider(client)
    start_pipeline(client, generator_config, data_provider, args.loglevel)
    logger.info("#### Generating data done! *Happy Face* ####")


def start_pipeline(carla_client, generator_config, data_provider, log_level):
    """Starts the pipeline and their steps

    :param carla_client: Reference to the connected carla client
    :type carla_client: object
    :param generator_config: Configuration of the generator
    :type generator_config: dict
    :param data_provider: Reference to the data provider caching instance
    :type data_provider: object
    """
    pipelines = generator_config["pipelines"]
    if generator_config["dataprovider"]["preload"]:
        logger.info("### START preloading data START ###")
        data_provider.preload()
        logger.info("### END preloading data END ###")
    logger.info("### Running pipelines... ###")
    for pipeline in pipelines:
        pipeline_name = extract_pipeline_name(pipeline)
        logger.info(f'## START pipeline "{pipeline_name}" START ##')
        tree = initialize_xml_tree()
        pipeline_config = extract_pipeline_config(pipeline)
        classes = get_plugin_classes_in_configured_order(pipeline_config["steps"])
        for idx, Class in enumerate(classes):
            logger.info(f'# START pipeline step #{idx} {Class.__name__} START #')
            step_config = pipeline_config["steps"][idx]
            if not isinstance(step_config, dict):
                step_config = dict()
            else:
                step_config = list(step_config.values())[0]
            instance = Class(carla_client, step_config, data_provider, idx,
                             get_plugin_logger(Class.__name__, log_level))
            instance.generate(tree)
            logger.info(f'# END pipeline step #{idx} {Class.__name__} END #')
        write_xml(tree, filename=pipeline_name)
        logger.info(f'## END pipeline "{pipeline_name}" END ##')


def get_args():
    """Parses the command line arguments and sets defaults where necessary

    :returns: The parsed arguments
    :rtype: object
    """
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
    argparser.add_argument(
        '--config',
        metavar='C',
        default='config.yaml',
        help='Configuration file (default: config.yaml)')
    argparser.add_argument(
        '--loglevel',
        metavar='L',
        default=logging.INFO,
        help='Logging level of output, eg. DEBUG (default: INFO)')
    return argparser.parse_args()


if __name__ == "__main__":
    main()
