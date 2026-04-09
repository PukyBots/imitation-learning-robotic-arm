# Remote Digital Sequencing (WiFi WebUI)

![Remote Digital Sequencing](banner.jpeg)

This module facilitates remote operation of the robotic arm over a WiFi connection. Users can interact with a web-based dashboard on any device (laptop, tablet, phone) connected to the same network.

## Features
- **Wireless Connection**: Untethered control through local network communication.
- **Web UI Dashboard**: Adjust robotic joints and orchestrate complex sequences from a central interface.
- **Digital Sequencing**: Design and trigger macro sequences of movements dynamically.

## How to Run
1. Upload the `controller.ino` to an ESP32 or ESP8266 microcontroller configured for your network.
2. Make sure the robot and the host machine are on the same WiFi network.
3. Run the Flask server: `python app.py`
4. Access the web interface from any device's browser using the host's local IP address.
