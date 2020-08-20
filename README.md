# Pre Crash Scenario Generator

## Table of Contents
* [Getting Started](#getting-started)
* [Useful Links](#useful-links)
* [Scenarios](#scenarios)

## Getting Started
To get started, you need to install the [CARLA simulator](https://carla.org/) as well as the [scenario runner](https://github.com/carla-simulator/scenario_runner). If you go for the windows version, you don't necessarily need to build CARLA on your own, but you can make use of the [prebuilt releases](https://github.com/carla-simulator/carla/releases). The version used for this project is ``0.9.9``, which is the newest development version.

## Useful Links
+ [CARLA Driving Challenge](https://carlachallenge.org/challenge/nhtsa/)
+ Scenario Runner
    + [Repository](https://github.com/carla-simulator/scenario_runner)
    + [Get Scenario Runner](https://github.com/carla-simulator/scenario_runner/blob/master/Docs/getting_scenariorunner.md)
    + [Getting Started](https://github.com/carla-simulator/scenario_runner/blob/master/Docs/getting_started.md)
    + [List of example scenarios](https://github.com/carla-simulator/scenario_runner/blob/master/Docs/list_of_scenarios.md)

## Scenarios
The [carla challenge](https://carlachallenge.org/) provides [10 of the most occuring pre-crash scenarios](https://carlachallenge.org/challenge/nhtsa/) as illustrations. As the scenario-runner documentation lacks a proper mapping of these scenarios to the example scenarios, a mapping can be found in the [scenarioMapping](scenarioMapping.txt) as a key-value-pairing.

The values provided, are the filenames in which the configurations of these scenarios are in. As an example ``Traffic03:ObjectCrossing``, where ``ObjectCrossing`` is the filename in ``<scenario-runner-root>/srunner/examples`` and ``Traffic03`` is the scenario number coming from the carla challenge. Inside of the configuration file, you will find scenarios of type ``StationaryObjectCrossing`` and of type ``DynamicObjectCrossing``. Both are valid start scenarios to run with eg. ``python scenario_runner.py --scenario DynamicObjectCrossing_1 --reloadWorld --timeout 30`` (mind the ``_1`` after the scenarioname, as there are multiple ones).
