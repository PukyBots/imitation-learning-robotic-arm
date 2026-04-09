# 🕹️ ArmFlow — Web Control Hub

**ArmFlow** is the software brain of the Imitation Learner project. It is a Python/Flask web application that runs on your computer and provides a sleek browser-based interface to control, teach, and replay movements on a 6-axis robotic arm.

---

## 📁 Directory Structure

```
ArmFlow/
├── app.py              # Flask backend — all logic, routes, and state lives here
├── static/
│   ├── logo.png        # ArmFlow logo shown in the navbar
│   └── arm.png         # Decorative arm image on the hero section
└── templates/
    └── index.html      # The entire Single-Page frontend Application (SPA)
```

---

## ⚙️ Backend: `app.py`

This is the master controller. It manages all connections and acts as the **translation layer** between the web interface and the physical hardware.

### Key Responsibilities

| Responsibility | How |
|---|---|
| Serve the frontend UI | Flask renders `index.html` at the `/` route |
| Auto-discover the ESP32 | Pings every IP on the local subnet concurrently using `ping3` |
| Send real-time commands | Sends comma-separated angle strings over **UDP** (Wi-Fi) or **Serial** (USB) |
| Read from Master Robot | Polls the `myCobot` joint angles every 50ms in a background thread |
| Record & Playback | Stores lists of joint angle snapshots in memory (`saved_moves`) |

### System State

The app maintains a global `sys_state` dictionary which tracks the current operational mode:

```python
sys_state = {
    "connection": "wifi",     # "wifi" or "wired"
    "mode": "wifi_ui_rec",    # Active control mode string
    "is_playing": False,      # True when replaying a recorded sequence
    "speed_delay": 25         # ms delay per degree of servo movement (safety)
}
```

### API Endpoints

| Method | Endpoint | What it Does |
|---|---|---|
| `GET` | `/` | Serves the main web page |
| `GET` | `/api/scan` | Scans the local network for active devices and returns their IPs & hostnames |
| `GET` | `/api/locate?ip=<IP>` | Pings the given IP to confirm an ESP32 is alive, then locks onto it as the target |
| `GET` | `/api/mode?m=<mode>&port=<PORT>` | Switches the active control mode. For `wired_ui_rec`, it opens the serial port. |
| `GET` | `/api/settings?p=speed_delay&v=<value>` | Updates a setting value (e.g., the movement speed delay) |
| `GET` | `/api/ui_move?a=<angles>` | Forwards slider values from the UI directly to the arm |
| `GET` | `/api/cobot_power?state=lock\|unlock` | Locks (powers on) or Unlocks (free-float) the myCobot motors |
| `POST` | `/api/action?cmd=<cmd>` | Executes a memory action: `record_ui`, `record_cobot`, `play`, or `clear` |
| `GET` | `/api/stop_actions` | Immediately halts any running memory playback |

### Data Packet Format
Every command sent to the ESP32 is a **7-value comma-separated string**:

```
Base, Shoulder, Elbow, WristPitch, WristRoll, Gripper, SpeedDelay
 90,      112,    68,         90,        90,       0,         25
```
All angle values are in the 0–180° range. `SpeedDelay` is clamped between 5–50ms for servo safety.

---

## 🖥️ Frontend: `index.html`

The entire user interface lives in a single HTML file. It is a **Single-Page Application (SPA)** using vanilla JS — no frameworks. Page transitions are handled by toggling CSS `hidden` classes.

### Visual Design System

The UI uses a warm **Dark Mode** color palette with an **Orange accent** (`#F97316`):

*   **Background**: Deep charcoal `#1C1C1C` with floating particle animations.
*   **Cards**: Slightly lighter `#2A2A2A` panels with subtle orange glows on hover.
*   **Accent**: `#F97316` (orange) for all interactive elements.
*   **Status bar**: Fixed at the very bottom; acts as a live system log.

---

---

## 🗺️ UI Walkthrough (Step-by-Step)

The interface is organized as a **3-step wizard** flow: Connect → Mode → Control.
Progress is tracked by the pill navigation bar at the top.

---

### Step 1 — Connect Tab

> **Goal**: Locate the robotic arm on the network.

The first page you see when you open `http://localhost:5000`.

**How to use it:**

1. Click **Scan Network** — ArmFlow will rapidly ping all devices on your Wi-Fi. Any live device will appear in a dropdown list.
2. Select the ESP32 from the dropdown (it will auto-fill the IP input), **or** type the IP manually (e.g., `192.168.1.45` or `roboarm.local`).
3. Click **Connect to Arm**. ArmFlow will verify the device is reachable and then advance you automatically to **Step 2: Mode Selection**.

---

### Step 2 — Mode Tab

> **Goal**: Choose how you want to control the arm.

This page presents 4 mode cards to choose from.

![Mode Selection Screen](screenshots/mode_selection.png)

| Mode Card | Type | Description |
|---|---|---|
| **Cobot Real-Time Mirror** | 📡 Wireless | Physically move the myCobot master arm. The target arm mirrors every movement live. |
| **Cobot Record Checkpoints** | 📡 Wireless | Move the myCobot to a pose, save it as a checkpoint, build a sequence, then replay. |
| **Web UI Record & Play** | 📡 Wireless | Use on-screen sliders to pose the arm. Snap waypoints and play them back. |
| **USB Record & Play** | 🔌 Wired USB | Same as Web UI mode but communicates via a direct USB cable for guaranteed low latency. |

**For the USB mode**, an additional input box slides open:
1. Plug a USB cable from your PC to the ESP32.
2. Type the COM port (e.g., `COM13`) into the text field.
3. Click **Confirm USB & Start**. ArmFlow sends a `SYS:WIRED` handshake to the ESP32, which will then shut off its Wi-Fi radio and switch to pure serial mode.

---

### Step 3 — Control Tab

> **Goal**: Operate the arm in real-time.

The control panel changes its contents depending on which mode you selected.

#### 🔧 Component Always Present: Movement Speed Slider

At the very top of Step 3, you always have the **Movement Speed** control.

![Control Panel - Cobot Live Mode](screenshots/control_live.png)

*   Drag the slider left for **Faster** movement (lower ms delay).
*   Drag right for **Slower, safer** movement (higher ms delay).
*   The badge on the right updates live: `Fast · 10ms`, `Normal · 25ms`, `Slow · 40ms`.
*   This value is sent as the **7th parameter** in every data packet to the ESP32.

> ⚠️ **Safety Note:** Moving too fast without physical limits may damage servos. Start slow and work down.

---

#### 🧭 UI: Web UI Record & Play Mode

This panel appears when you select **Web UI Record & Play** (Wireless or Wired).

![Control Panel - Web UI Record Mode](screenshots/control_ui_rec.png)

**6 Joint Sliders:**

| Joint | Default Angle | Range |
|---|---|---|
| Base | 90° | 0° – 180° |
| Shoulder | 112° | 0° – 180° |
| Elbow | 68° | 0° – 180° |
| Wrist P (Pitch) | 90° | 0° – 180° |
| Wrist R (Roll) | 90° | 0° – 180° |
| Gripper | 0° | 0° – 80° |

![6-Axis Joint Sliders](screenshots/joint_sliders.png)

Dragging **any slider** instantly sends the new angle packet to the ESP32. The physical arm moves in real-time as you slide.

**Recording a Motion Sequence:**
1. Drag the sliders to form the arm's first pose.
2. Click **Snap Waypoint** — the orange pin button saves the current 6-angle state to memory.
3. Adjust sliders for the next pose, snap another waypoint.
4. Repeat as many times as needed. The **Recorded Memory** counter shows how many frames are saved.
5. Hit the green **Play Memory** button. The arm will move through each waypoint sequentially with a 2.5-second hold per step.
6. Press the red **Clear** button to wipe the memory and start fresh.

---

#### 🤖 UI: Cobot Real-Time Mirror Mode

This panel appears when you select **Cobot Real-Time Mirror**.

![Control Panel - Cobot Live Mode](screenshots/control_live.png)

*   A green **"Live Mirroring Active"** badge pulses at the top, confirming the cobot thread is streaming.
*   **Unlock Motors**: Releases the myCobot's servo brakes so you can manually push/pull the arm to any pose (free-float mode). This is how you "teach" the robot!
*   **Lock Motors**: Powers the myCobot servos back on, locking it rigidly in place.

**Workflow:**
1. Click **Unlock Motors**.
2. Gently grasp the myCobot arm and move it to any desired position.
3. The target robotic arm mirrors the movement in real-time wirelessly.

---

#### 📍 UI: Cobot Record Checkpoints Mode

Similar to the Live Mirror mode, but adds checkpoint-based recording.

![Control Panel - Cobot Record Checkpoints](screenshots/control_cobot_rec.png)

*   **Unlock Motors** → physically pose the master arm.
*   Click **Save Checkpoint** → the current myCobot joint angles are frozen and saved to memory.
*   **Lock Motors** → re-lock the master arm.
*   Build as many checkpoints as you want, then click **Play Memory** to autonomously replay them.

---

### 🔵 The Status Bar

The thin bar at the very **bottom of every page** is your live system log:

```
● Wireless Mode Active
```

*   A **green dot** means the last operation was successful.
*   A **red dot** with an `✗` means an error occurred (e.g., `myCobot not found on PI.`, `No device found at 192.168.x.x`).
*   Messages update instantly as you perform actions.

---

### 💡 The About Modal

Click the **ⓘ (Info)** icon in the top-right corner to open the About panel. It gives:
*   A description of the project.
*   A quick summary of all 4 control modes.
*   The full technology stack used.
*   A link to the GitHub repository.

---

### 🌙 Theme Toggle

Click the **moon/sun icon** in the top-right corner to switch between the warm **Light Mode** and the sleek **Dark Mode**. Your preference is persisted in `localStorage` across browser sessions.

---

## 🐛 Common Issues & Solutions

| Problem | Likely Cause | Solution |
|---|---|---|
| `myCobot not found on PI.` in status bar | myCobot not physically connected or its port is wrong in `app.py` | Check `COBOT_PORT` constant in `app.py`. Disable cobot features if unused. |
| Scan finds no devices | ESP32 is on a different subnet or its Wi-Fi is off | Enter the IP address manually in Step 1. |
| Arm doesn't move after connecting | Wrong IP locked, or ESP32 isn't receiving UDP on port 5005 | Check Windows Firewall. Ensure both PC and ESP32 are on the same Wi-Fi. |
| USB Mode fails to open | Wrong COM port entered | Open Device Manager → Ports to find the correct COM port. |
| Playback is jumpy/skips poses | Speed delay is too low | Increase Movement Speed slider to `25ms` or higher for smooth playback. |
