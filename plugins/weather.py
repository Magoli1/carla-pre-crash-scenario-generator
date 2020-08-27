from xml.etree.ElementTree import SubElement
import random
import copy


class Weather:
    def __init__(self, carla_client, config):
        self.client = carla_client
        if "per_scenario" not in config:
            config["per_scenario"] = 1
        if config["per_scenario"] <= 0:
            raise Exception("Weather generators optional property 'per_scenario' cannot be <= 0")
        self.config = config

    def generate(self, tree):
        self.extend_scenarios(tree, self.config["per_scenario"] - 1)
        for scenario in tree.getroot().getchildren():
            weather = SubElement(scenario, "weather")
            self.generate_random_weather_with_defaults(weather)

    def extend_scenarios(self, tree, number_copies):
        if number_copies <= 0:
            return
        root = tree.getroot()
        children = root.getchildren()
        for idx, scenario in enumerate(children):
            for inner_idx in range(number_copies):
                new_scenario = copy.deepcopy(scenario)
                # TODO Naming could be enhanced
                new_scenario.set("name", f'{new_scenario.get("name")}-{inner_idx}')
                root.insert(idx + 1 + inner_idx + idx * number_copies, new_scenario)

    def generate_random_weather_with_defaults(self, weather_element):
        weather_element.set("cloudiness",
                            str(self.config.get("cloudiness", round(random.uniform(0, 100), 2))))
        weather_element.set("precipitation",
                            str(self.config.get("precipitation", round(random.uniform(0, 100), 2))))
        weather_element.set("precipitation_deposits", str(
            self.config.get("precipitation_deposits", round(random.uniform(0, 100), 2))))
        weather_element.set("wind_intensity", str(
            self.config.get("wind_intensity", round(random.uniform(0, 100), 2))))
        weather_element.set("sun_azimuth_angle", str(
            self.config.get("sun_azimuth_angle", round(random.uniform(0, 360), 2))))
        weather_element.set("sun_altitude_angle", str(
            self.config.get("sun_altitude_angle", round(random.uniform(-90, 90), 2))))
        weather_element.set("fog_density",
                            str(self.config.get("fog_density", round(random.uniform(0, 100), 2))))
        weather_element.set("fog_distance", str(self.config.get("fog_distance",
                                                                round(random.uniform(0, 100),
                                                                      2))))  # max could be infinite
        weather_element.set("wetness",
                            str(self.config.get("wetness", round(random.uniform(0, 100), 2))))
        weather_element.set("fog_falloff",
                            str(self.config.get("fog_falloff", round(random.uniform(0, 5), 2))))
