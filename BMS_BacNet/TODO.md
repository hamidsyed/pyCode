# Sensor Parameter Update - TODO List

## Progress Tracker

### File 1: bms_simulator.py
- [x] Update class docstring to reflect 6 new sensors
- [x] Replace sensor_data dictionary with 6 new sensors
- [x] Replace sensor_metadata dictionary with new ranges and units
- [x] Rewrite _update_sensors() method with new simulation logic
- [x] Update print statement format
- [x] Update example usage in __main__

### File 2: bms_bacnet_server_bacnet.py
- [x] Update _add_sensors_as_objects() - change to 6 sensors
- [x] Update sensor definitions with new names and units
- [x] Update _update_loop() sensor_map
- [x] Update docstrings and comments

### File 3: bms_bacnet_client_bacnet.py
- [x] Update read_all_sensors() mapping (5 to 6 sensors)
- [x] Update print format for 6 sensors
- [x] Update comments

### File 4: bms_bacnet_demo_bacnet.py
- [x] Update to read new sensor
- [x] Update comments

### File 5: BMS_BACNET_DOC.md
- [x] Update Overview section
- [x] Update sensor list documentation
- [x] Update instance mappings (1-6)
- [x] Update examples

## Summary

All files have been successfully updated with the new 6-sensor configuration:
✓ bms_simulator.py - Core simulator updated with new sensors and ranges
✓ bms_bacnet_server_bacnet.py - BACnet server exposing 6 analog objects
✓ bms_bacnet_client_bacnet.py - Client reading all 6 sensors
✓ bms_bacnet_demo_bacnet.py - Demo updated to showcase all sensors
✓ BMS_BACNET_DOC.md - Documentation fully updated

The system now simulates:
1. Total Electricity Energy (0-600 kWh)
2. Outdoor Air Drybulb Temperature (5-44°C)
3. Outdoor Air Relative Humidity (11-100%)
4. Wind Speed (0-9.3 m/s)
5. Diffuse Solar Radiation (0-444 W/m²)
6. Direct Solar Radiation (0-924 W/m²)

## New Sensor Specifications
1. Total Electricity Energy: 0-600 kWh
2. Outdoor Air Drybulb Temperature: 5-44°C
3. Outdoor Air Relative Humidity: 11-100%
4. Wind Speed: 0-9.3 m/s
5. Diffuse Solar Radiation: 0-444 W/m²
6. Direct Solar Radiation: 0-924 W/m²
