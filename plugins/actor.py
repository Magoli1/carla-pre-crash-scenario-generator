from xml.etree.ElementTree import Element


class Actor:
    def __init__(self, carla_client, config):
        self.client = carla_client
        self.config = config

    def generate(self, tree):
        pass
