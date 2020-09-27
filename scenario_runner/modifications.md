# ScenarioRunner Enhancements
In the following the files are listed which have been extended with additional features.

`srunner/scenarioconfigs/scenario_configuration.py`
- Added parsing of the `color` attribute for actors

`srunner/scenariomanager/carla_data_provider.py`
- Fixed the format of the default color

`srunner/scenarios/follow_leading_vehicle.py`
- Added reading the model and color of the other actor from config

`srunner/scenarios/no_signal_junction_crossing.py`
- Added reading color of the other actor from config

`srunner/scenarios/opposite_vehicle_taking_priority.py`
- Added reading color of the other actor from config

`srunner/scenarios/signalized_junction_left_turn.py`
- Added reading color of the other actor from config

`srunner/scenarios/signalized_junction_right_turn.py`
- Added reading color of the other actor from config

`srunner/scenarios/object_crash_vehicle.py`
- Added random static object instead of only vendingmachine
