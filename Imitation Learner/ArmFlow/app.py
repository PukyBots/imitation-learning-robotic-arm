import socket
import serial
import time
import threading
import concurrent.futures
from ping3 import ping
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# ==========================================
# ⚙️ SYSTEM STATE & SETTINGS
# ==========================================
target_ip = None
target_port = 5005
udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
esp_serial = None

sys_state = {
    "connection": "wifi", 
    "mode": "wifi_ui_rec",
    "is_playing": False,
    "speed_delay": 25  # Default safe movement delay (ms per degree)
}

saved_moves = []
current_cobot_payload = None 

# 🤖 Connect to myCobot
COBOT_PORT = '/dev/ttyAMA0'
try:
    from pymycobot.mycobot import MyCobot
    mc = MyCobot(COBOT_PORT, 1000000)
    mc.release_all_servos()
    cobot_available = True
    print("✅ myCobot connected.")
except Exception as e:
    mc = None
    cobot_available = False
    print("⚠️ myCobot not found on PI.")

# ==========================================
# 📡 NETWORK SCANNER
# ==========================================
def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

def check_ip(ip):
    if ping(ip, timeout=0.2):
        try:
            hostname = socket.gethostbyaddr(ip)[0]
            if hostname.endswith('.local'): hostname = hostname[:-6]
        except Exception:
            hostname = "Unknown Device"
        return {"ip": ip, "name": hostname}
    return None

def scan_network():
    my_ip = get_local_ip()
    if my_ip == '127.0.0.1': return []
    network_prefix = ".".join(my_ip.split('.')[:-1])
    active_devices = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        ips_to_check = [f"{network_prefix}.{i}" for i in range(1, 255)]
        results = executor.map(check_ip, ips_to_check)
        for result in results:
            if result: active_devices.append(result)
    return active_devices

# ==========================================
# 🔄 CORE ROUTING & MATH
# ==========================================
def send_to_esp(payload_str):
    if sys_state["is_playing"]: return
    
    # We now append the 7th parameter (speed_delay) before sending!
    final_payload = f"{payload_str},{int(sys_state['speed_delay'])}"
    
    if sys_state["connection"] == "wifi" and target_ip:
        try:
            udp_socket.sendto(final_payload.encode('utf-8'), (target_ip, target_port))
        except: pass
    elif sys_state["connection"] == "wired" and esp_serial:
        try:
            esp_serial.write(f"{final_payload}\n".encode('utf-8'))
        except: pass

def map_angle(val, in_min, in_max, out_min, out_max):
    mapped = (val - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
    return max(min(int(mapped), out_max), out_min)

def cobot_thread():
    global current_cobot_payload
    while True:
        if cobot_available and "cobot" in sys_state["mode"] and not sys_state["is_playing"]:
            angles = mc.get_angles()
            if angles and len(angles) >= 5:
                # Map -90 to +90 over to standard 0 to 180
                base     = map_angle(angles[0], -90, 90, 0, 180)
                shoulder = map_angle(angles[1], -90, 90, 0, 180)
                elbow    = map_angle(angles[2], -90, 90, 0, 180)
                w_pitch  = map_angle(angles[3], -90, 90, 0, 180)
                w_roll   = map_angle(angles[4], -90, 90, 0, 180)
                
                # We save only the 6 angles here. Speed is appended inside send_to_esp
                payload_str = f"{base},{shoulder},{elbow},{w_pitch},{w_roll},0"
                current_cobot_payload = payload_str 
                send_to_esp(payload_str)
                
        time.sleep(0.05)

threading.Thread(target=cobot_thread, daemon=True).start()

# ==========================================
# 🌐 WEB DASHBOARD
# ==========================================
# ==========================================
# 🌐 FLASK API ENDPOINTS
# ==========================================
@app.route('/')
def index(): return render_template('index.html')

@app.route('/api/scan')
def api_scan():
    return jsonify({"devices": scan_network()})

@app.route('/api/locate')
def locate():
    global target_ip
    ip = request.args.get('ip')
    
    if ip.endswith(".local"):
        try:
            target_ip = socket.gethostbyname(ip)
            return jsonify({"success": True, "msg": f"✅ Resolved to {target_ip}"})
        except:
            return jsonify({"success": False, "msg": f"❌ Could not resolve {ip}"})
            
    try:
        response = ping(ip, timeout=0.5)
        if response is None or response is False:
            return jsonify({"success": False, "msg": f"❌ No device found at {ip}."})
    except: pass

    target_ip = ip
    return jsonify({"success": True, "msg": f"✅ Locked onto {target_ip}"})

@app.route('/api/mode')
def mode():
    global esp_serial, sys_state
    m = request.args.get('m')
    port = request.args.get('port')
    
    if "cobot" in m and not cobot_available:
        return jsonify({"success": False, "msg": "❌ myCobot not found on PI."})
        
    sys_state["mode"] = m
    
    if m == "wired_ui_rec":
        sys_state["connection"] = "wired"
        if target_ip:
            try:
                udp_socket.sendto(b"SYS:WIRED", (target_ip, target_port))
                time.sleep(1) 
            except: pass
        try:
            esp_serial = serial.Serial(port, 115200, timeout=0.1)
            return jsonify({"success": True, "msg": f"🔌 USB Mode Active ({port})"})
        except Exception as e:
            return jsonify({"success": False, "msg": f"❌ USB Error: {str(e)}"})
    else:
        sys_state["connection"] = "wifi"
        if esp_serial and esp_serial.is_open: esp_serial.close()
        return jsonify({"success": True, "msg": f"📡 Wireless Mode Active"})

@app.route('/api/settings')
def settings():
    p = request.args.get('p')
    v = float(request.args.get('v'))
    sys_state[p] = v
    return "OK"

@app.route('/api/cobot_power')
def cobot_power():
    if not cobot_available: return jsonify({"msg": "❌ Cobot not connected"})
    state = request.args.get('state')
    if state == 'lock':
        mc.power_on()
        return jsonify({"msg": "🔒 Motors Locked"})
    else:
        mc.release_all_servos()
        return jsonify({"msg": "🔓 Motors Unlocked (Free move)"})

@app.route('/api/ui_move')
def ui_move():
    if "ui" in sys_state["mode"]: send_to_esp(request.args.get('a'))
    return "OK"

@app.route('/api/stop_actions')
def stop_actions():
    sys_state["is_playing"] = False
    return "OK"

@app.route('/api/action', methods=['GET', 'POST'])
def handle_action():
    global saved_moves, sys_state, current_cobot_payload
    cmd = request.args.get('cmd')
    
    if cmd == 'record_ui':
        saved_moves.append(list(request.json['angles']))
        return jsonify({"msg": "📍 Waypoint Saved", "count": len(saved_moves)})
        
    elif cmd == 'record_cobot':
        if current_cobot_payload:
            saved_moves.append(current_cobot_payload.split(','))
            return jsonify({"msg": "📍 Checkpoint Saved", "count": len(saved_moves)})
        return jsonify({"msg": "⚠️ No data from Cobot yet"})
        
    elif cmd == 'clear':
        saved_moves.clear()
        return jsonify({"msg": "🗑️ Cleared", "count": 0})
        
    elif cmd == 'play':
        if not saved_moves: return jsonify({"msg": "⚠️ Memory Empty!"})
        sys_state["is_playing"] = True
        
        # Since we use Checkpoints now, give the robot 2.5 seconds to glide to each point
        playback_pause = 2.5 
        
        for step in saved_moves:
            if not sys_state["is_playing"]: break 
            
            # Reconstruct the payload and append the CURRENT speed limit setting
            payload = ",".join(map(str, step[:6])) + f",{int(sys_state['speed_delay'])}"
            
            if sys_state["connection"] == "wifi":
                udp_socket.sendto(payload.encode('utf-8'), (target_ip, target_port))
            elif sys_state["connection"] == "wired" and esp_serial:
                esp_serial.write(f"{payload}\n".encode('utf-8'))
                
            time.sleep(playback_pause)
            
        sys_state["is_playing"] = False
        return jsonify({"msg": "✅ Playback Complete"})
        
    return jsonify({"msg": "Unknown"})

if __name__ == '__main__':
    print("🚀 Master Hub Started! Open http://0.0.0.0:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)