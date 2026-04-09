#include <WiFi.h>
#include <WiFiUdp.h>
#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>
#include <WiFiManager.h>
#include <ESPmDNS.h>

unsigned int localPort = 5005;

#define I2C_SDA 21
#define I2C_SCL 22

Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver();
WiFiUDP Udp;
char packetBuffer[255];

#define SERVOMIN 150
#define SERVOMAX 600

// Defaults to 25. Will be updated dynamically by the Python UI!
int MOVEMENT_DELAY = 25; 

double currentAngle[6] = {90, 112, 68, 90, 90, 0}; 
int targetAngle[6]     = {90, 112, 68, 90, 90, 0}; 
unsigned long lastMoveTime = 0;

bool isWifiActive = true; 

void setup() {
  Serial.begin(115200);
  Wire.begin(I2C_SDA, I2C_SCL);
  pwm.begin();
  pwm.setPWMFreq(50);
  delay(500);

  for(int i = 0; i < 6; i++) {
     int pulse = map(currentAngle[i], 0, 180, SERVOMIN, SERVOMAX);
     pwm.setPWM(i, 0, pulse);
  }
  
  WiFiManager wifiManager;
  Serial.println("Connecting to saved Wi-Fi, or starting Setup Portal...");
  
  bool connected = wifiManager.autoConnect("RoboArm_Setup");
  
  if(!connected) {
    Serial.println("Failed to connect and hit timeout. Rebooting...");
    delay(3000);
    ESP.restart();
  }

  Serial.println("\n✅ Connected to Home Wi-Fi!");
  Serial.print("📡 Assigned IP ADDRESS: ");
  Serial.println(WiFi.localIP()); 
  
  if (!MDNS.begin("roboarm")) {
    Serial.println("Error setting up MDNS responder!");
  } else {
    Serial.println("✅ mDNS responder started at: roboarm.local");
  }

  Udp.begin(localPort);
  Serial.println("🎧 Listening on UDP (Wi-Fi) and USB Serial...");
}

void processInput(char* inputString) {
  if (strncmp(inputString, "SYS:WIRED", 9) == 0) {
    Serial.println("\n⚠️ [SYSTEM] Handshake received. Shutting down Wi-Fi radio...");
    isWifiActive = false;
    WiFi.disconnect(true);
    WiFi.mode(WIFI_OFF);
    Serial.println("🔌 Wi-Fi OFF. Now operating exclusively over USB Wired Serial.");
    return;
  }
  
  if (strncmp(inputString, "SYS:WIFI", 8) == 0) {
    Serial.println("\n⚠️ [SYSTEM] Rebooting to restore Wi-Fi...");
    delay(500);
    ESP.restart(); 
  }

  // 🧠 THE NEW PARSER: Handles the 7th Speed Parameter
  char *token = strtok(inputString, ",");
  int i = 0;
  while (token != NULL) {
    int val = atoi(token);
    
    if (i < 5) {
      targetAngle[i] = constrain(val, 0, 180); // Arm joints
    } 
    else if (i == 5) {
      targetAngle[i] = constrain(val, 0, 80);  // Gripper
    } 
    else if (i == 6) {
      // THIS IS THE NEW SPEED DELAY (Locks between 5ms and 50ms for safety)
      MOVEMENT_DELAY = constrain(val, 5, 50); 
    }
    
    token = strtok(NULL, ",");
    i++;
  }
}

void loop() {
  if (isWifiActive) {
    int packetSize = Udp.parsePacket();
    if (packetSize) {
      int len = Udp.read(packetBuffer, 255);
      if (len > 0) {
        packetBuffer[len] = 0; 
        processInput(packetBuffer);
      }
    }
  }

  if (Serial.available() > 0) {
    String input = Serial.readStringUntil('\n');
    input.trim();
    if (input.length() > 0) {
      char serialBuffer[255];
      input.toCharArray(serialBuffer, 255);
      processInput(serialBuffer);
    }
  }

  // Uses the new, dynamic MOVEMENT_DELAY sent from the website!
  if (millis() - lastMoveTime > MOVEMENT_DELAY) {
    lastMoveTime = millis();
    for (int i = 0; i < 6; i++) {
      if ((int)currentAngle[i] != targetAngle[i]) {
        if (currentAngle[i] < targetAngle[i]) currentAngle[i] += 1;
        else currentAngle[i] -= 1;
        int pulse = map((int)currentAngle[i], 0, 180, SERVOMIN, SERVOMAX);
        pwm.setPWM(i, 0, pulse);
      }
    }
  }
}