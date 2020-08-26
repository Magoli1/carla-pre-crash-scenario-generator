from xml.etree.ElementTree import SubElement


class Weather:
    def __init__(self, carla_client, config):
        self.client = carla_client
        if "mode" not in config:
            raise Exception("Weather generator property 'mode' is mandatory")
        mode_possible_values = ["random", "constant"]
        if config["mode"] not in mode_possible_values:
            raise Exception(
                f'Weather generator value of mandatory property "mode" needs to be in {mode_possible_values}')
        self.config = config

    def generate(self, tree):
        children = tree.getroot().getchildren()
        #for idx, scenario in enumerate(children):
        #    weather = SubElement(scenario, "weather")
        #    weather.set("name", f'{self.config["name_prefix"]}{idx}')
        #    weather.set("type", self.config["type"])
        #    weather.set("town", town)

#    def generate_constant_weather(self, weather_element):


