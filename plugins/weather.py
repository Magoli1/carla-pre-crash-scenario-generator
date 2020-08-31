from xml.etree.ElementTree import SubElement
import random
import carla

from core.helpers.utils import extend_scenarios


class Weather:
    def __init__(self, carla_client, config, data_provider):
        self.client = carla_client
        if "per_scenario" not in config:
            config["per_scenario"] = 1
        if config["per_scenario"] <= 0:
            raise Exception("Weather generators optional property 'per_scenario' cannot be <= 0")
        self.config = config
        self.data_provider = data_provider
        self.carla_weather_presets = ["ClearNoon", "CloudyNoon", "WetNoon", "WetCloudyNoon",
                                      "SoftRainNoon", "MidRainyNoon", "HardRainNoon",
                                      "ClearSunset", "CloudySunset", "WetSunset",
                                      "WetCloudySunset", "SoftRainSunset", "MidRainSunset",
                                      "HardRainSunset"]

    def generate(self, tree):
        extend_scenarios(tree, self.config["per_scenario"] - 1)
        for scenario in tree.getroot().getchildren():
            weather = SubElement(scenario, "weather")
            self.decorate_weather_random_with_defaults(weather)

    def decorate_weather_random_with_defaults(self, weather_element):
        weather_config = vars(carla.WeatherParameters)[random.choice(self.carla_weather_presets)]
        weather_element.set("cloudiness",
                            str(self.config.get("cloudiness", weather_config.cloudiness)))
        weather_element.set("precipitation",
                            str(self.config.get("precipitation", weather_config.precipitation)))
        weather_element.set("precipitation_deposits",
                            str(self.config.get("precipitation_deposits", weather_config.precipitation_deposits)))
        weather_element.set("wind_intensity",
                            str(self.config.get("wind_intensity", weather_config.wind_intensity)))
        weather_element.set("sun_azimuth_angle",
                            str(self.config.get("sun_azimuth_angle", weather_config.sun_azimuth_angle)))
        weather_element.set("sun_altitude_angle",
                            str(self.config.get("sun_altitude_angle", weather_config.sun_altitude_angle)))
        weather_element.set("fog_density",
                            str(self.config.get("fog_density", weather_config.fog_density)))
        weather_element.set("fog_distance",
                            str(self.config.get("fog_distance", weather_config.fog_distance)))  # max could be # infinite
        weather_element.set("wetness",
                            str(self.config.get("wetness", weather_config.wetness)))
        weather_element.set("fog_falloff",
                            str(self.config.get("fog_falloff", weather_config.fog_falloff)))
