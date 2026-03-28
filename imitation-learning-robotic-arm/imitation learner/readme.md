# 🦾 ArmFlow

> **A multi-mode robotic arm control system for teleoperation, kinesthetic teaching, and imitation learning.**

![ArmFlow Banner](docs/banner.png)

[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)]()
[![ESP32](https://img.shields.io/badge/ESP32-Firmware-orange.svg)]()
[![Status](https://img.shields.io/badge/Project-Active-brightgreen.svg)]()

---

## ✨ Overview

ArmFlow is a leader-follower robotic arm platform built to demonstrate **teleoperation**, **kinesthetic teaching**, and **imitation learning** in a clean browser-based interface.

A **myCobot 280** acts as the leader arm, while a custom **ESP32 + PCA9685** follower arm executes the movements. The Python Flask hub sits in the middle like the conductor of a small robotic orchestra, coordinating live mirroring, checkpoint recording, and playback.

---

## 🚀 Key Features

* **Live Wireless Mirroring**: Real-time joint angle mapping from the leader arm to the follower arm over UDP.
* **Kinesthetic Teaching**: Unlock the myCobot, move it by hand, and save learned poses as checkpoints.
* **Record & Play Mode**: Store sequences of joint positions and replay them smoothly.
* **Wired USB Fallback**: Stable serial control when Wi-Fi is weak or unavailable.
* **Modern Web UI**: Browser-based control panel with a responsive layout.
* **Safety Controls**: Angle limiting, smooth stepping, and movement delay tuning to protect servos.

---

## 🧠 How It Works

ArmFlow uses a **leader-follower** architecture:

1. **Leader Arm**
   The myCobot 280 provides the source joint angles.

2. **Python Hub**
   A Flask server reads the myCobot data, maps the angles, and sends compact control payloads.

3. **Follower Arm**
   The ESP32 receives the payload through UDP or Serial, then drives the servos through the PCA9685 PWM controller.

Instead of sending heavy JSON data, ArmFlow uses a lightweight comma-separated payload:

```text
base,shoulder,elbow,pitch,roll,gripper,speed_delay
```

Example:

```text
90,112,68,90,90,0,25
```

---

## 🏗️ System Architecture

### Leader Node

* **Hardware**: Elephant Robotics myCobot 280
* **Role**: Captures joint angles and supports kinesthetic teaching

### Control Hub

* **Backend**: Flask + Python
* **Role**: UI server, network scanning, angle mapping, playback logic, device routing

### Follower Node

* **Microcontroller**: ESP32
* **Motor Driver**: PCA9685 16-channel PWM driver
* **Actuators**: 6 servos
* **Role**: Executes motion commands smoothly and safely

---

## 🧰 Technology Stack

### Backend

* Python
* Flask
* PySerial
* Ping3
* Pymycobot
* Socket / UDP

### Firmware

* C++
* ESP32 Arduino Core
* Adafruit PWM Servo Driver Library
* WiFiManager
* ESPmDNS

### Frontend

* HTML
* CSS
* Vanilla JavaScript

---

## 🔌 Hardware Wiring

### ESP32 to PCA9685

| ESP32 Pin   | PCA9685 Pin |
| ----------- | ----------- |
| 3V3         | VCC         |
| GND         | GND         |
| GPIO 21     | SDA         |
| GPIO 22     | SCL         |
| External 5V | V+          |

### Important Notes

* Use a **separate 5V power supply** for servos.
* Do **not** power all servos directly from the ESP32.
* Keep GND common between the ESP32 and servo power supply.

---

## 📦 Installation

### 1) Clone the repository

```bash
git clone https://github.com/YourUsername/ArmFlow.git
cd ArmFlow
```

### 2) Install Python dependencies

```bash
pip install Flask pyserial ping3 pymycobot
```

### 3) Flash the ESP32 firmware

* Open the ESP32 firmware file in Arduino IDE
* Install the required libraries:

  * Adafruit PWM Servo Driver Library
  * WiFiManager
* Flash the firmware to the board

### 4) Connect the hardware

* Connect the ESP32 to the PCA9685
* Power the servos with an external supply
* Connect the myCobot to the computer running Flask

---

## ▶️ Running the Project

Start the Flask server:

```bash
python app.py
```

Then open the web interface in your browser:

```text
http://localhost:5000
```

If the server is running on another machine, use its local IP address instead.

---

## 🎛️ Control Modes

### 1. Wireless Live Mirroring

The myCobot streams joint positions to the ESP32 through UDP for real-time motion matching.

### 2. Wireless Checkpoints

Save key poses and replay them later over Wi-Fi.

### 3. UI Record

Use the web interface to manually create movement sequences.

### 4. Wired USB

Send commands through Serial for a reliable tethered connection.

---

## 🧩 Core Logic

### Angle Mapping

The myCobot angle range is translated into the servo-friendly range used by the follower arm.

### Smooth Motion Loop

The ESP32 does not jump directly to target angles. Instead, it moves in small steps using a non-blocking timing loop, producing smoother motion and reducing stress on the hardware.

### Lightweight Communication

Using a simple string payload keeps packet parsing fast on the microcontroller and reduces latency.

### Checkpoint Memory

Saved poses are stored as an array of joint states and replayed in order during playback.

---

## 📁 Suggested Project Structure

```text
ArmFlow/
├── app.py
├── requirements.txt
├── firmware/
│   └── esp32_armflow.ino
├── static/
│   ├── css/
│   └── js/
├── templates/
│   └── index.html
├── docs/
│   └── banner.png
└── README.md
```

---

## 🛡️ Safety Features

* Angle constraining to prevent invalid servo commands
* Movement delay tuning for safer motion
* Dedicated servo power supply to reduce brownout risk
* Motor unlock/lock support during kinesthetic teaching

---

## 🔮 Future Improvements

* Computer vision integration for object detection
* Inverse kinematics support using XYZ coordinates
* Cloud-based telemetry and sequence storage
* Better motion planning and path smoothing
* More advanced UI analytics and live feedback

---

## 🖼️ Screenshots

> Add screenshots here to make the README more visual.

```markdown
![Dashboard](docs/screenshot-dashboard.png)
![Hardware Setup](docs/screenshot-hardware.png)
![Playback Mode](docs/screenshot-playback.png)
```

---

## 🤝 Contributing

Contributions, ideas, and improvements are welcome.

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Open a pull request

---

## 📄 License

This project is licensed under the MIT License.

---

## 🙏 Acknowledgements

* Elephant Robotics for the myCobot platform
* Open-source libraries and tools used in the build
* Everyone who helped shape the project into a working robotic system
