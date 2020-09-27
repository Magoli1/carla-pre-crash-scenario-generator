# Pre Crash Scenario Generator

## Table of Contents
* [Getting Started](#getting-started)
    * [Prerequisites](#prerequisites)
    * [Configuration Entities](#configuration-entities)
* [Concept](#concept)
* [Write your own plugin](#write-your-own-plugin)
* [Advanced Usage](#advanced-usage)
    * [Data Provider](#data-provider)
    * [Helper Utils](#helper-utils)
* [Scenarios](#scenarios)
* [Tools](#tools)
    * [Showing Spawnpoints and Waypoints of Intersections](#showing-spawnpoints-and-waypoints-of-intersections)
* [Generate the code documentation](#generate-the-code-documentation)
* [Useful Links](#useful-links)

## Getting Started
To get started, you first need to install the [prerequisites](#prerequisites). After that you can start to use the generator with the provided ``config.yaml`` in the root folder. It has all scenarios from the [carla challenge](https://carlachallenge.org/) available. All properties which are available are documented [here](#configuration-entities), so you can easily build your own configuration.

Start the generator by using the ``generator.py`` file in the project root. You can specifiy several connection properties for the carla simulator directly via the command line.
### Prerequisites
To get started, you need to install the [CARLA simulator](https://carla.org/) as well as the [scenario runner](https://github.com/carla-simulator/scenario_runner). If you go for the windows version, you don't necessarily need to build CARLA on your own, but you can make use of the [prebuilt releases](https://github.com/carla-simulator/carla/releases). The version used for this project is ``0.9.9``, which is the newest development version. 

### Configuration Entities
The following entities are available out of the box to be used in the configuration file.
#### Dataprovider
The ``data_provider`` entity is an *optional* configuration entry. Enabling the ``preload`` property lets the data provider preload **all** long running data fetch tasks, before the actual pipeline steps will run. Not enabling it, will lazy load the data when it is requested by the pipeline steps. Both approaches ultimately lead to the same output, but they can differ in runtime, as the lazy loading will only fetch data, that is really requested by the pipeline plugins, instead of all available data (more info [here](#data-provider)).
```yaml
dataprovider:
  preload: True # Default: False
```
#### Pipelines
The ``pipeline`` entity is a mandatory configuration entry. The generator expects a valid list of pipelines, so you need to supply at least one. The name can be freely chosen and is used as the XML-output filename.
```yaml
pipelines:
  - ControlLoss_generated:
    steps:
       ...
  - FollowLeadingVehicle_generated:
    steps:
       ...
  - ObjectCrossing_generated:
    steps:
       ...
```
#### Plugins
You are able to define the pipeline steps via the extensible plugin system (more on this [here](#write-your-own-plugin)). To provide basic functionality we provide three different plugins for direct usage. You are also free to extend those depending on your needs. It is also possible to specify multiple plugins of the same type after each other, eg. if you would like to have multiple *actors*.

##### Scenario
The Scenario plugin creates the ``scenario`` tag with the attributes ``name`` and ``type``, as well as the ``town``. As a mandatory configuration entry, you need to add the *type*. The *name_prefix* will be defaulted to ``type<idx>``, where *idx* is the index of the generated scenario, but you can also provide your own. The plugin will use all to carla available maps and it generates one entry per map. You can optionally specify the ``map_blacklist`` to exclude specific maps with their *simple name*.
```yaml
- Scenario:
    name_prefix: Test
    type: ControlLoss
    map_blacklist:
      - Town01
      - Town02
```

##### Actor
The Actor plugin can be used for any kind of actor like vehicles or walkers. In the default case, the actor plugin is configured to generate *ego_vehicle* tags with vehicles from the blueprint library. When supplying the ``per_scenario`` attribute, you can multiply the aready created scenarios from the former pipeline steps. It is also possible to supply the ``tag`` name that the plugin writes into the xml, eg. if you would like to use ``other_actor`` as a tag. You can also change the type of actor, that is used for the *model* attribute, by changing the ``type``. To position the actors, you can configure the ``positioning`` for *junctions* and/or *streets*.
```yaml
- Actor:
    per_scenario: 5 # optional, default 1
    tag: ego_vehicle # optional, default ego_vehicle
    type: vehicle # optional, default vehicle
    positioning: # optional, default junctions: True, streets: True
        junctions: False
        streets: True
```

##### Weather
The weather plugin generates for every scenario inside the XML-tree the ``weather`` tag. You can optionally specifiy the ``per_Scenario`` property, which is defaulted to 1. By giving it a higher number, you multiply the already existing entries inside the XML by this number. This makes it possible to have the same scenario several times, each time, with different weather behaviors. By specifying the optional property ``generation_type``, you can change the behavior of generated weather scenarios. Possible values are *random_preset* and *random*. The default is *random_preset*. In case of that value, the already available presets from carla are used for the weather scenarios. When you specify *random*, each variable of the weather attribute will be randomly selected on its own. The provided example will result in 4 copies of the input scenarios, so that there are 5 scenarios.
```yaml
- Weather:
    per_scenario: 5
    generation_type: random
```

## Concept
The goal of this project is to generate carla scenario variations in a simple and efficient way. To achieve this goal, the core of the generator will take care about all the bits and pieces that you as a developer don't want to deal with, when generating the scenario variations. This includes writing the XML file, loading the plugins and its classes, as well as building the generation pipeline.

Besides the core, the generator is extensible via [plugins](#plugins). These plugins can be configured in a yaml file in the root of the project. This way, it's simple to influence the generation process. The efficiency aspect is tightly interconnected with the configuration entities. Here you are able to define your plugins multiple times. Thus you don't need to write multiple plugins that share the same logic. You only need to make the plugin enough configurable from the outside. This is further underlined by the powerful caching system that you have access to inside the plugins.

Dealing with multiple different scenario variations on different maps with different behaviors can be a hustle. To make this workload easily manageable, the software is able to generate multiple variations and thus runs multiple pipelines in one run. In this case, one pipeline is defined as a list of plugins, that are called after each other. Each plugin is able to perform actions on the XML tree. During the execution, a plugin gets the altered tree of its predecessor.

In contrast to that, pipelines are strictly decoupled from each other. This is done for the reason that different scenarios don't have any cross-dependencies between each other, so the pipelines also don't have them.
## Write your own plugin
To make the generator easily extensible, you are able to write plugins, that are automatically available inside the pipelines after configuring them inside the ``.yaml`` configuration file. To do that you need to follow these steps:

1. Create a new *.py file in the ``plugins/`` folder
2. Create a class with a naming you like (*Hint: The naming of the class needs to be globally unique, so it is not allowed that there is another class in some other file with the same name*). This name will be used in the pipeline as an identifier for your plugin
3. Implement the *\_\_init\_\_* method (see below). You will get passed the following data:
    * carla client with already opened connection to the simulator
    * The configuration for your pipeline step
    * The data_provider object, which you can use to access cached data entities (more [here](#data-provider))
    * The index of the step that this plugin is running (*Note: For every step inside the pipelines a new object will get created for the plugin, even if it is multiple times inside*)
    * The custom logger instance (see more [here](#logging))
    ```python
    def __init__(self, carla_client, config, data_provider, step_idx, logger):
        pass
    ```
4. Implement the *generate* method (see below). You dont need to return anything as the xml-tree works with pointers for faster processing. You will get passed the following data:
    * The XML-tree with all scenario inside, which got generated in the steps before.
    ```python
    def generate(self, tree):
        pass
    ```
## Advanced Usage
To enhance the workflows during generation scenarios, this generator implements some advanced mechanics and helper methods, which make sure that the generation of scenarios runs as fast and as efficiently as possible.

### Data Provider
As described [here](#dataprovider), the data provider gives you a powerful method for caching data that takes time to get. You will get access to the data provider by using the passed object as shown [here](#write-your-own-plugin). There are currently two data entities that can be accessed by using the following methods:
1. *get_waypoints_per_map*: This will give you a dict of map names with another dict as value, which has the keys *junctions* and *streets*. Both of them have as a value a list of waypoints which are at a junction or on a street.
2. *get_available_maps_simple_name*: As the name suggests, this methods gives you all simple names (*not fully qualified*) of all available maps.

### Helper Utils
To make regular tasks easy, we provide the following helper methods that can be imported inside of the plugins:
1. *extend_scenarios*: This method copies the scenario tags the given number of times. It automatically takes care about naming the entities in a unique way, when copying all attributes of the tag.
2. *change_map*: As the name suggests, this lets you change the map of the carla simulator. In comparison to the native carla method for changing maps, this method gives you the ability to specify the timeout for loading new maps. It is also defaulted in such a way that also "slow" computers will work with it.
3. *is_full_qualified_map_name*: Checks whether the provided map name is in the fully qualified format or not.
4. *get_simple_map_name*: Given a fully qualified name, it will give you the simple name of a map, which is the last part of the fully qualified name.

### Logging
A custom logging instance is passed to the constructor of every plugin. It can be used to log any output to stdout. This also applies to errors, which can be logged with ``logger.error``. They will be marked red inside of the console for better visibility. It is on you to break the execution with ``raise SystemExit(0)`` or to just give the information and let the pipeline run further.


## Scenarios
The [carla challenge](https://carlachallenge.org/) provides [10 of the most occuring pre-crash scenarios](https://carlachallenge.org/challenge/nhtsa/) as illustrations. As the scenario-runner documentation lacks a proper mapping of these scenarios to the example scenarios, a mapping can be found in the [scenarioMapping](scenarioMapping.txt) as a key-value-pairing.

The values provided, are the filenames in which the configurations of these scenarios are in. As an example ``Traffic03:ObjectCrossing``, where ``ObjectCrossing`` is the filename in ``<scenario-runner-root>/srunner/examples`` and ``Traffic03`` is the scenario number coming from the carla challenge. Inside of the configuration file, you will find scenarios of type ``StationaryObjectCrossing`` and of type ``DynamicObjectCrossing``. Both are valid start scenarios to run with eg. ``python scenario_runner.py --scenario DynamicObjectCrossing_1 --reloadWorld --timeout 30`` (mind the ``_1`` after the scenarioname, as there are multiple ones).

## Tools 
We provide several powerful tools, that are helpful in order to develop new features or to visualize interesting entities on the maps.

### Showing Spawnpoints and Waypoints of Intersections
By running the python file **show_spawn_and_way_points.py** you can see all spawnpoints and all waypoits which belong to a certain junction. 

## Generate the code documentation
The projects code documentation is written in docstring and is making use of [Sphinx](https://www.sphinx-doc.org/en/master/index.html). Before generating the documentation, make sure you have installed all requirements. Then run the following commands:
```shell script
cd docs
make html
```

## Useful Links
+ [CARLA Driving Challenge](https://carlachallenge.org/challenge/nhtsa/)
+ Scenario Runner
    + [Repository](https://github.com/carla-simulator/scenario_runner)
    + [Get Scenario Runner](https://github.com/carla-simulator/scenario_runner/blob/master/Docs/getting_scenariorunner.md)
    + [Getting Started](https://github.com/carla-simulator/scenario_runner/blob/master/Docs/getting_started.md)
    + [List of example scenarios](https://github.com/carla-simulator/scenario_runner/blob/master/Docs/list_of_scenarios.md)
