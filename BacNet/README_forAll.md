# Project File Summaries

This file provides a summary of all the files in the project.

## Core Files

### `bms_bacnet_client_bacnet.py`

A BACnet client implemented using the `bacpypes` library. This client can read `presentValue` from AnalogValue objects from a BACnet server. It also includes a `DBHandler` class to store the readings in a SQLite or PostgreSQL database.

### `bms_bacnet_client.py`

A simple TCP socket-based client for reading sensor data from the `bms_bacnet_server`. It can read single sensor values, all sensor values, and device information.

### `bms_bacnet_server.py`

A TCP socket-based server that exposes sensor data from a `BMSDevice` instance. It handles multiple clients using threading and communicates via a JSON-based protocol.

### `bms_simulator.py`

This file is not in the provided list, but it's a core component of the system. It simulates a Building Management System (BMS) device with multiple sensors like temperature, humidity, pressure, CO2 level, and occupancy.

### `bms_monitor.py`

A monitoring system for BMS devices. It can collect data from multiple devices, log the data to CSV or JSON files, calculate statistics, and generate alerts based on predefined thresholds.

## Examples and Demos

### `bms_complete_example.py`

This script provides a complete demonstration of the BMS system, running the server and client in parallel threads. It includes several demo scenarios, such as an integrated server-client demo, a simple monitoring demo, and a manual sensor control demo.

### `bms_demo.py`

An interactive script that allows users to run different demonstrations of the BMS system. It provides a menu to choose between demos like standalone BMS device operation, BMS with a BACnet server, manual sensor control, and monitoring multiple devices.

### `bms_test.py`

A test suite for the BMS system. It includes tests for the `BMSDevice`, `BMSServer`, and `BMSClient` to ensure all components are working correctly.

## Documentation

### `BMS_README.md`

The main documentation file for the project. It provides a comprehensive overview of the BMS simulator, including its features, installation instructions, usage examples, API reference for all the main classes, and network configuration details.

### `COMPLETION_REPORT.md`

A detailed report marking the completion of the project. It summarizes the deliverables, provides project statistics, lists implemented features, and describes the technical architecture.

### `DEMO_STEPS.md`

A step-by-step guide on how to run the various demos included in the project. It provides commands and expected outputs for each demo scenario.

### `INDEX.md`

An index of all project files, providing a quick overview of each file's purpose. It also includes quick commands to run tests and demos.

### `PROJECT_SUMMARY.md`

A high-level summary of the project. It covers the project overview, deliverables, key features, technical specifications, and test results.

### `QUICKSTART.md`

A guide for new users to get started with the project quickly. It includes simple code examples, an architecture overview, and troubleshooting tips.

## Requirements

### `requirements_bacnet.txt`

This file lists the Python dependencies required for the BACnet-specific parts of the project, which is the `bacpypes` library.

### `requirements_bms.txt`

This file lists the Python dependencies for the core BMS simulator, which may include libraries like `numpy`.
