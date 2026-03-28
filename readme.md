<div align="center">

![ArmFlow — Robotic Arm that Learns from Demonstration](ArmFlow.jpeg)

# ArmFlow — Imitation Learning Robotic Arm

**A 6-DOF robotic arm that learns tasks by watching you do them.**  
Control it wirelessly, teach it movements physically, then let it replay them autonomously.

[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-Web%20Server-000000?style=flat&logo=flask)](https://flask.palletsprojects.com)
[![ESP32](https://img.shields.io/badge/ESP32-Firmware-E7352C?style=flat&logo=espressif)](https://espressif.com)
[![Arduino](https://img.shields.io/badge/Arduino-IDE-00979D?style=flat&logo=arduino)](https://arduino.cc)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat)](LICENSE)

</div>

---

## 🧭 What Is This Project?

**ArmFlow** is an end-to-end imitation learning platform for a custom-built 6-axis robotic arm. The project bridges hardware, embedded systems, networking, and a modern web interface into one seamless system.

The core idea is simple: **demonstrate a task, record it, replay it**. Instead of programming a robot with lines of code for every movement, you simply move a master robot (or use a web interface), and ArmFlow records the motion. One click later, the arm performs the task autonomously — exactly as you showed it.

This project covers four distinct control modes, each a step up in complexity and capability:

| # | Mode | Type | Teach Method |
|---|---|---|---|
| 1 | Tethered Precision Control | Wired USB | Web UI sliders |
| 2 | Remote Digital Sequencing | Wireless Wi-Fi | Web UI sliders |
| 3 | Wireless Teleoperation | Wireless Wi-Fi | Physical cobot mirroring |
| 4 | Kinesthetic Teaching | Wireless Wi-Fi | Physical cobot checkpoints |

---

## 📁 Project Structure

```
interview/
├── ArmFlow.jpeg                          # Project title banner
├── readme.md                             # ← You are here (Overall docs)
│
├── Imitation Learner/                    # 🏆 Final unified system (all 4 modes combined)
│   ├── controller.ino                    # ESP32 firmware (unified, handles all modes)
│   ├── readme.md                         # Detailed setup + visual walkthrough
│   ├── images/                           # Connection walkthrough diagrams
│   │   ├── img1.jpeg                     # WiFiManager onboarding flow
│   │   ├── img2.jpeg                     # Web UI search & connect flow
│   │   ├── img3.jpeg                     # Mode selection architecture diagram
│   │   └── img4.jpeg                     # All 4 control panels side-by-side
│   └── ArmFlow/                          # Flask web application
│       ├── app.py                        # Backend — all APIs, state, and logic
│       ├── readme.md                     # ArmFlow app-specific docs
│       ├── static/
│       │   ├── logo.png                  # Navbar logo
│       │   └── arm.png                   # Hero section arm image
│       └── templates/
│           └── index.html               # Full single-page frontend (SPA)
│
└── imitation-learning-robotic-arm/       # 📚 Individual mode prototypes (dev history)
    ├── 1.Tethered Precision Control ( USB - WEBUI )/
    ├── 2.Remote Digital Sequencing ( WiFi - WEBUI )/
    ├── 3.Wireless Teleoperation ( REALTIME - COBOT )/
    └── 4.Kinesthetic Teaching ( REC&PLAY - COBOT )/
```

---

## 🧱 System Architecture

The system is composed of three hardware/software layers that talk to each other in real time:

```
┌─────────────────────────────────────────────────────────────────┐
│                      YOUR COMPUTER                              │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Browser (index.html)  ←→  Flask Server (app.py)        │   │
│  │  • Slider controls          • Network scanner           │   │
│  │  • Mode selection           • UDP socket sender         │   │
│  │  • Record / Play UI         • Serial port manager       │   │
│  └─────────────────────────┬───────────────────────────────┘   │
└────────────────────────────┼────────────────────────────────────┘
                             │  Wi-Fi (UDP port 5005)
                             │  or USB Serial (115200 baud)
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                   ESP32 MICROCONTROLLER                         │
│  • Receives: "Base,Shoulder,Elbow,WristP,WristR,Gripper,Speed" │
│  • Parses comma-separated angles                                │
│  • Interpolates servos 1° per tick at SpeedDelay interval      │
│  • Communicates with PCA9685 over I2C (GPIO 21/22)             │
└──────────────────────────────┬──────────────────────────────────┘
                               │  I2C (SDA=GPIO21, SCL=GPIO22)
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│              PCA9685 PWM SERVO DRIVER BOARD                     │
│  • Drives 6 servo channels (ch0–ch5)                           │
│  • Maps 0–180° angles to 150–600 PWM pulse width               │
│  • 50Hz PWM frequency for standard hobby servos                │
└─────────────────────────────────────────────────────────────────┘
```

**Optional hardware path (Teleoperation modes):**
```
myCobot 280 (Master)  →  pymycobot (Serial)  →  Flask cobot_thread  →  ESP32 (Target)
```

---

## 🛠️ Full Technology Stack

### Hardware
| Component | Part | Role |
|---|---|---|
| Microcontroller | ESP32 Dev Board | Wi-Fi, Serial, mDNS, firmware logic |
| Servo Driver | PCA9685 (I2C, 16-ch) | Drives all 6 servo motors |
| Actuators | 6× MG996R Servos | Physical joints of the arm |
| Master Robot | Elephant Robotics myCobot 280 | Physical teacher for Modes 3 & 4 |
| Power | External 5–6V regulated supply | Servo power rail (separate from ESP32) |

### Software
| Layer | Technology | Purpose |
|---|---|---|
| Backend | Python 3.8+ / Flask | API server, state manager, network hub |
| Networking | `socket`, `ping3` | Concurrent IP scanning, UDP sender |
| Serial | `pyserial` | USB wired connection to ESP32 |
| Cobot | `pymycobot` | Reads live joint angles from myCobot |
| Frontend | Vanilla HTML5 / CSS3 / JS | Single-page control UI, no frameworks |
| Icons | Lucide Icons (CDN) | Scalable modern icon set |
| Fonts | Google Fonts (Inter, Playfair) | Typography system |
| Firmware | C++ / Arduino Core (ESP32) | Servo interpolation, command parser |
| Wi-Fi Setup | WiFiManager (tzapu) | Captive portal for credential-free setup |
| Servo Control | Adafruit PWM Servo Driver | I2C communication with PCA9685 |

### Data Protocol
Every command sent to the ESP32 is a **7-value comma-separated string**:
```
90,112,68,90,90,0,25
 ▲    ▲   ▲   ▲   ▲  ▲  ▲
 │    │   │   │   │  │  └─ SpeedDelay (ms, clamped 5–50)
 │    │   │   │   │  └──── Gripper (0–80°)
 │    │   │   │   └─────── Wrist Roll (0–180°)
 │    │   │   └─────────── Wrist Pitch (0–180°)
 │    │   └─────────────── Elbow (0–180°)
 │    └─────────────────── Shoulder (0–180°)
 └──────────────────────── Base (0–180°)
```

---

## 🔌 Mode 1 — Tethered Precision Control (USB + Web UI)

![Mode 1 — Tethered Precision Control](imitation-learning-robotic-arm/1.Tethered%20Precision%20Control%20%28%20USB%20-%20WEBUI%20%29/banner.png)

**The entry point.** A direct, wired, no-Wi-Fi-needed control mode. The ESP32 is connected to your computer via USB. The web interface sends servo commands over the serial port at 115200 baud. Zero network setup. Zero packet loss. Maximum reliability.

**How it works:**
1. Flash `controller.ino` to the ESP32 and connect it via USB.
2. Run `app.py` in the `1.Tethered...` folder.
3. Open `http://localhost:5000` in your browser.
4. Enter the COM port (e.g. `COM13`) in the interface.
5. Use the 6 on-screen sliders to control each joint in real time.
6. Click **Record** to snapshot the current pose as a waypoint.
7. Click **Play** to replay all saved waypoints in sequence.

**Signal path:**
```
Browser Slider → HTTP GET /ui_move → Flask → pyserial.write() → USB → ESP32 → Servos
```

**Best for:** Testing hardware, precise debugging, lab environments with USB access.

---

## 📡 Mode 2 — Remote Digital Sequencing (Wi-Fi + Web UI)

![Mode 2 — Remote Digital Sequencing](imitation-learning-robotic-arm/2.Remote%20Digital%20Sequencing%20%28%20WiFi%20-%20WEBUI%20%29/banner.png)

**Go wireless.** Identical control to Mode 1 but over Wi-Fi using UDP packets. The ESP32 joins your home/lab network and Flask sends angle data as UDP datagrams to port 5005. This eliminates the USB cable, allowing the arm to be placed anywhere within network range.

**How it works:**
1. Flash the firmware and power on the ESP32. Use the WiFiManager captive portal (`RoboArm_Setup`) to connect it to your Wi-Fi.
2. Run `app.py` and open the web UI.
3. Click **Scan Network** — Flask pings all 254 addresses in your subnet concurrently and lists live devices.
4. Select the ESP32's IP address (or type `roboarm.local`) and click **Connect**.
5. Use sliders, record waypoints, play sequences — exactly like Mode 1 but wirelessly.

**Signal path:**
```
Browser Slider → HTTP GET /ui_move → Flask → UDP socket → Wi-Fi → ESP32 → Servos
```

**Best for:** Clean setups where the arm needs freedom of movement, demos, and presentations.

---

## 🤖 Mode 3 — Wireless Teleoperation (Real-Time Cobot Mirror)

![Mode 3 — Wireless Teleoperation](imitation-learning-robotic-arm/3.Wireless%20Teleoperation%20%28%20REALTIME%20-%20COBOT%20%29/banner.png)

**Become the robot.** A second robotic arm — the **myCobot 280** — acts as a physical input controller. Flask reads its joint angles every 50ms via serial using the `pymycobot` library, translates them from the cobot's -90°/+90° range to the servo's 0°–180° range, and immediately fires a UDP packet to the ESP32. The target arm mirrors every physical movement of the master arm in real time.

**How it works:**
1. Connect the myCobot 280 to your Raspberry Pi or computer via serial.
2. Run `app.py` (which starts the `cobot_thread` background daemon automatically).
3. Connect to the ESP32 wirelessly via the web UI.
4. Select **Cobot Real-Time Mirror** mode.
5. Click **Unlock Motors** on the myCobot so you can physically move it by hand.
6. Grab the master arm and move it — the output arm copies every motion live.

**Signal path:**
```
Your Hand → myCobot joints → pymycobot (Serial) → Flask cobot_thread → UDP → ESP32 → Servos
```

**Angle mapping:**
```python
# myCobot outputs -90° to +90°
# Target servos expect 0° to 180°
servo_angle = (cobot_angle - (-90)) * (180 / 180)
```

**Best for:** Live demonstrations, haptic teleoperation, remote control scenarios.

---

## 🧠 Mode 4 — Kinesthetic Teaching (Record & Play via Cobot)

![Mode 4 — Kinesthetic Teaching](imitation-learning-robotic-arm/4.Kinesthetic%20Teaching%20%28%20REC%26PLAY%20-%20COBOT%20%29/banner.png)

**The heart of imitation learning.** You physically pose the master arm, save that pose as a checkpoint, move to the next pose, save again — building a complete motion sequence through pure physical demonstration. Then click **Play**, and the target arm executes the entire learned sequence autonomously.

This is **kinesthetic teaching** — the same principle used in modern industrial robotics and robot learning research. No code. No angles typed. You teach by doing.

**How it works:**
1. Connect the myCobot and ESP32 (same as Mode 3).
2. Select **Cobot Record Checkpoints** mode in the web UI.
3. **Unlock Motors** on the myCobot.
4. Physically move the master arm to the starting position of your task.
5. Click **Save Checkpoint** — the current joint angles are captured and stored in memory.
6. Move the arm to the next position in the sequence. Save another checkpoint.
7. Repeat until the full task is recorded.
8. Click **Play Memory** — the target arm travels through every checkpoint with smooth servo interpolation.

**Signal path (Recording):**
```
Your Hand → myCobot joints → pymycobot → Flask → saved_moves[] (RAM)
```

**Signal path (Playback):**
```
saved_moves[i] → Flask → UDP → ESP32 → Servos  (2.5s pause per checkpoint)
```

**Best for:** Teaching repetitive tasks (pick-and-place, assembly), imitation learning research, AI data collection.

---

## 📸 Connection Walkthrough — From First Boot to Full Control

These four images walk through the complete connection flow — from the ESP32's first power-on to executing a learned motion sequence.

---

### Step A — ESP32 First-Time Wi-Fi Setup

![ESP32 WiFiManager Captive Portal Setup](Imitation%20Learner/images/img1.jpeg)

When the ESP32 boots for the first time with no Wi-Fi credentials saved, it creates its own temporary Wi-Fi hotspot called **`RoboArm_Setup`**. Here is what each panel shows:

- **Panel 1 (Left):** Your device's Wi-Fi list. `RoboArm_Setup` appears as a normal network. The "Action needed, no internet" label is correct — this is a private local setup network.
- **Panel 2 (Center):** On connecting, open `http://192.168.4.1` in your browser. The `WiFiManager` library serves this page automatically. Click **Configure WiFi** to begin.
- **Panel 3 (Right):** A live scan of nearby Wi-Fi networks appears. Select yours, enter the password, and click **Save**. The ESP32 reboots and joins your local network permanently. It registers itself via mDNS as `roboarm.local`.

> This one-time process never needs to be repeated unless the ESP32 is factory-reset.

---

### Step B — Web UI: Search, Discover & Connect to the Arm

![ArmFlow Web UI — Scan, Select, Connect](Imitation%20Learner/images/img2.jpeg)

Once `app.py` is running and your browser is open at `http://localhost:5000`, this is the **Step 1: Connect** screen. The flow has three sub-phases:

- **INITIATE (Search):** Click **Scan Network**. Flask spawns 50 concurrent threads using `ThreadPoolExecutor`, each pinging one IP address in your subnet. A full 254-address scan completes in seconds. Each live device is resolved to a hostname via `socket.gethostbyaddr()`.
- **SELECT (Discover):** The dropdown populates with results. `10.185.51.60 (ESP32-Arm)` is the target arm. The `192.168.4.x (Setup)` entries are ESP32s still broadcasting their first-time hotspot. Select the correct device; the IP field auto-fills.
- **CONTROL (Connect):** Click **Connect to Arm**. Flask calls `/api/locate`, pings the IP to confirm it is alive, locks it as `target_ip`, and the UI advances automatically to Step 2.

---

### Step C — Web UI: Choose Your Drive Mode

![ArmFlow Mode Selection — Architecture Diagram](Imitation%20Learner/images/img3.jpeg)

The **Step 2: Mode Selection** page shows all 4 control cards alongside an architecture diagram that maps the full physical data path for each:

| Mode | Data Path |
|---|---|
| Cobot Real-Time Mirror | Hand → myCobot → Serial → Flask → UDP → ESP32 → Arm |
| Cobot Record Checkpoints | Hand → myCobot → Flask RAM → (On Play) UDP → ESP32 → Arm |
| Web UI Record & Play | Browser Sliders → HTTP → Flask → UDP → ESP32 → Arm |
| USB Record & Play | Browser Sliders → HTTP → Flask → USB Serial → ESP32 → Arm |

The diagram makes the architecture immediately clear: the left side is always the human input (cobot or browser), the center is always the Flask hub on your computer, and the right side is always the physical arm.

---

### Step D — Web UI: Step 3 — All 4 Control Panels

![ArmFlow Control Panels — All 4 Modes](Imitation%20Learner/images/img4.jpeg)

This image shows all four Step 3 control panels side-by-side, one for each mode:

- **Mode 1 (Mirroring, top-left):** The `cobot_thread` status shows `[ACTIVE]`. A joint scaling slider adjusts the 1:1 ratio. The **Disconnect** button pauses the live stream.
- **Mode 2 (Checkpoints, top-right):** A spatial grid map visualises each saved checkpoint (P1, P2, P3). The **Record Checkpoint** and **Replay Sequence** buttons build and execute the motion sequence.
- **Mode 3 (Web UI, bottom-left):** Six virtual joint sliders for all articulations. A **REC** button saves each pose. A **PLAY** button replays all saved waypoints. Waypoint count shown live.
- **Mode 4 (USB Serial, bottom-right):** A COM port dropdown (`COM3`, `COM4`, `COM5`). A **CONNECT** button opens the serial port. **START CONTROL** is locked until the serial handshake is confirmed.

---

## 🚀 Quick Start (Final System)

### Prerequisites
- Python 3.8+ installed
- Arduino IDE with ESP32 board support
- Node.js not required (pure vanilla frontend)

### 1. Flash the ESP32
```
1. Open: Imitation Learner/controller.ino in Arduino IDE
2. Install libraries via Library Manager (Ctrl+Shift+I):
   - "Adafruit PWM Servo Driver Library"
   - "WiFiManager" by tzapu
3. Select board: ESP32 Dev Module
4. Upload via USB
```

### 2. Hardware Wi-Fi Setup
```
1. Power on ESP32
2. Connect to "RoboArm_Setup" Wi-Fi
3. Open http://192.168.4.1 → Configure WiFi
4. Select your network, enter password, Save
5. Reconnect your PC to your normal Wi-Fi
```

### 3. Install & Run the Hub
```bash
cd "Imitation Learner/ArmFlow"
pip install flask pyserial ping3 pymycobot
python app.py
```

### 4. Open the Control UI
```
Open browser → http://localhost:5000
Step 1: Scan Network → Select ESP32 → Connect to Arm
Step 2: Choose your control mode
Step 3: Control, teach, and play back your sequence
```

---

## 🔮 Future Roadmap

As shown in the project banner, the planned next steps include:

| Feature | Description |
|---|---|
| **Inverse Kinematics (IK)** | Specify a target XYZ coordinate; the system calculates the required joint angles automatically |
| **YOLO Object Detection** | Camera-based object recognition to trigger and aim arm movements at detected targets |
| **OpenCV Computer Vision** | Visual feedback loop for closed-loop control and error correction |
| **ROS Integration** | Migrate to the Robot Operating System for modularity, simulation, and research compatibility |
| **Natural Language Interface** | Voice or text command parsing (e.g. "pick up the red block") using an LLM |
| **Dynamic Path Planning** | Real-time obstacle avoidance using sensor data during arm movement |
| **Swarm Intelligence** | Coordinate multiple arms on a shared network for collaborative tasks |

---

## 📄 Sub-Module Documentation

For deeper technical details, refer to the individual documentation files:

| Document | Covers |
|---|---|
| [`Imitation Learner/readme.md`](Imitation%20Learner/readme.md) | Full PRD, architecture, setup guide, visual connection walkthrough |
| [`Imitation Learner/ArmFlow/readme.md`](Imitation%20Learner/ArmFlow/readme.md) | `app.py` API endpoints, `index.html` UI walkthrough, troubleshooting |

---

<div align="center">

**Built with 🔶 by Sadath Ali Rahman**  
*Imitation Learning · Robotics · Embedded Systems · Full-Stack UI*

</div>
