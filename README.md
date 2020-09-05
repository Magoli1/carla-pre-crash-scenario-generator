# Pre Crash Scenario Generator

## Table of Contents
* [Getting Started](#getting-started)
    * [Prerequisites](#prerequisites)
    * [Configuration Entities](#configuration-entities)
* [Concept](#concept)
* [Scenarios](#scenarios)
* [Tools](#tools)
    * [Showing Spawnpoints and Waypoints of Intersections](#showing-spawnpoints-and-waypoints-of-intersections)
* [Useful Links](#useful-links)

## Getting Started
To get started, you first need to install the [prerequisites](#prerequisites). After that you can start to use the generator with the provided ``config.yaml`` in the root folder. It has all scenarios from the [carla challenge](https://carlachallenge.org/) available. All properties which are available are documented [here](#configuration-entities), so you can easily build your own configuration.

Start the generator by using the ``generator.py`` file in the project root. You can specifiy several connection properties for the carla simulator directly via the command line.
### Prerequisites
To get started, you need to install the [CARLA simulator](https://carla.org/) as well as the [scenario runner](https://github.com/carla-simulator/scenario_runner). If you go for the windows version, you don't necessarily need to build CARLA on your own, but you can make use of the [prebuilt releases](https://github.com/carla-simulator/carla/releases). The version used for this project is ``0.9.9``, which is the newest development version. 

### Configuration Entities
#### Dataprovider
The ``data_provider`` entity is an *optional* configuration entry. Enabling the ``preload`` property lets the data provider preload **all** long running data fetch tasks, before the actual pipeline steps will run. Not enabling it, will lazy load the data when it is requested by the pipeline steps. Both approaches ultimately lead to the same output, but they can differ in runtime, as the lazy loading will only fetch data, that is really requested by the pipeline plugins, instead of all available data.
```
dataprovider:
  preload: True # Default: False
```
#### Pipelines
The ``pipeline`` entity is a mandatory configuration entry. The generator expects a valid list of pipelines, so you need to supply at least one. The name can be freely chosen and is used as the XML-output filename.
```
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
The Scenario plugin creates the ``scenario`` tag with the attributes ``name`` and ``type``, as well as the ``town``. As a mandatory configuration entry, you need to add the *type*. The *name_prefix* will be defaulted to ``type<idx>``, where *idx* is the index of the generated scenario, but you can also provide your own. The plugin will use all to carla available maps and it generates one entry per map.
```
- Scenario:
    name_prefix: Test
    type: ControlLoss
```
##### Actor
The Actor plugin can be used for any kind of actor like vehicles or walkers. In the default case, the actor plugin is configured to generate *ego_vehicle* tags with vehicles from the blueprint library. When supplying the ``per_scenario`` attribute, you can multiply the aready created scenarios from the former pipeline steps. It is also possible to supply the ``tag`` name that the plugin writes into the xml, eg. if you would like to use ``other_actor`` as a tag. You can also change the type of actor, that is used for the *model* attribute, by changing the ``type``. To position the actors, you can configure the ``positioning`` for *junctions* and/or *streets*.
```
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
```
- Weather:
    per_scenario: 5
    generation_type: random
```
## Concept
## Write your own plugin

## Scenarios
The [carla challenge](https://carlachallenge.org/) provides [10 of the most occuring pre-crash scenarios](https://carlachallenge.org/challenge/nhtsa/) as illustrations. As the scenario-runner documentation lacks a proper mapping of these scenarios to the example scenarios, a mapping can be found in the [scenarioMapping](scenarioMapping.txt) as a key-value-pairing.

The values provided, are the filenames in which the configurations of these scenarios are in. As an example ``Traffic03:ObjectCrossing``, where ``ObjectCrossing`` is the filename in ``<scenario-runner-root>/srunner/examples`` and ``Traffic03`` is the scenario number coming from the carla challenge. Inside of the configuration file, you will find scenarios of type ``StationaryObjectCrossing`` and of type ``DynamicObjectCrossing``. Both are valid start scenarios to run with eg. ``python scenario_runner.py --scenario DynamicObjectCrossing_1 --reloadWorld --timeout 30`` (mind the ``_1`` after the scenarioname, as there are multiple ones).

## Tools 
We provide several powerful tools, that are helpful in order to develop new features or to visualize interesting entities on the maps.
### Showing Spawnpoints and Waypoints of Intersections
By running the python file **show_spawn_and_way_points.py** you can see all spawnpoints and all waypoits which belong to a certain junction. 

## Useful Links
+ [CARLA Driving Challenge](https://carlachallenge.org/challenge/nhtsa/)
+ Scenario Runner
    + [Repository](https://github.com/carla-simulator/scenario_runner)
    + [Get Scenario Runner](https://github.com/carla-simulator/scenario_runner/blob/master/Docs/getting_scenariorunner.md)
    + [Getting Started](https://github.com/carla-simulator/scenario_runner/blob/master/Docs/getting_started.md)
    + [List of example scenarios](https://github.com/carla-simulator/scenario_runner/blob/master/Docs/list_of_scenarios.md)
