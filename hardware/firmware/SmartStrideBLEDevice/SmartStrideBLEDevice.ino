#include <Adafruit_MPU6050.h>
#include <Adafruit_SSD1306.h>
#include <Adafruit_Sensor.h>
#include "BluetoothSerial.h"

// Bluetooth Serial communication
BluetoothSerial ESP_BT;

int incoming;

String speedStr = "";
String angleStr = "";

bool isSecond = false;

// MPU6050 and OLED display objects
Adafruit_MPU6050 mpu;
Adafruit_SSD1306 display = Adafruit_SSD1306(128, 64, &Wire);

// Variables for gyro readings and angle calculation
float gyro_z = 0;
float prev_gyro_z = 0;
float angle = 0; // Inclination angle of the treadmill

// Timestamp for time difference calculation
unsigned long prevTime = 0;

// Values for treadmill track
float trackCircumference = 3.31; // Circumference of the treadmill track in meters
const int sensorPins[] = {15, 2, 4, 18, 19}; // Sensor pins for detecting treadmill rotations

// Buffer for Bluetooth communication
char buffer[12];

// Rotation start time and counting flag
unsigned long rotationStartTime = 0;
unsigned long lastRotationTime = 0;
bool countingStarted = false;
int patch = 0;

void setup() {
  Serial.begin(19200);
  ESP_BT.begin("SmartStride_BT");

  // Initialize MPU6050 sensor
  if (!mpu.begin()) {
    Serial.println("Sensor init failed");
    while (1) yield(); // Pause indefinitely
  }
  Serial.println("Found a MPU-6050 sensor");

  // Initialize OLED display
  if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) { // Address 0x3C for 128x64
    Serial.println(F("SSD1306 allocation failed"));
    for (;;) ; // Loop indefinitely
  }

  // Display initialization
  display.display();
  delay(500); // Pause for 0.5 seconds
  display.setTextSize(2);
  display.setTextColor(WHITE);
  display.setRotation(0);

  // Initial display message
  display.clearDisplay();
  display.setCursor(0, 0);
  display.println("SmartStride");
  display.println("Bluetooth Not Connected");
  display.display();

  // Setting up MPU6050
  if (!mpu.begin()) {
    Serial.println("Failed to find MPU6050 chip");
    while (1) {
      delay(10);
    }
  }

  mpu.setAccelerometerRange(MPU6050_RANGE_16_G);
  mpu.setGyroRange(MPU6050_RANGE_250_DEG);
  mpu.setFilterBandwidth(MPU6050_BAND_21_HZ);

  Serial.println("MPU6050 initialized");

  // Initialize sensor pins
  for (int i = 0; i < 5; i++) {
    pinMode(sensorPins[i], INPUT);
  }
  Serial.println("Startup Done");
}


void loop() {
  // Check for available Bluetooth data
  // if (ESP_BT.available()) {
  incoming = ESP_BT.read(); //Read what we receive 

  display.clearDisplay();
  display.setCursor(0, 0);
  display.println("SmartStride");
  display.println("Bluetooth Connected");
  display.display();

  // Get sensor events with the readings
  sensors_event_t a, g, temp;
  mpu.getEvent(&a, &g, &temp);

  // Calculate time difference since last loop iteration
  unsigned long currentTime = millis();
  float dt = (currentTime - prevTime) / 1000.0;
  prevTime = currentTime;

  // Integrate gyroscope readings to calculate angle
  angle += (gyro_z + g.gyro.z) * dt / 2.0;

  // Update gyro_z and prev_gyro_z
  gyro_z = g.gyro.z;
  prev_gyro_z = gyro_z;


  // Sum sensor values to detect treadmill rotations
  int sumSensorValues = 0;
  for (int i = 0; i < 5; i++) {
    sumSensorValues += digitalRead(sensorPins[i]);
  }

  // Check for treadmill rotation and start counting
  if (sumSensorValues > 1 && !countingStarted && patch%2 == 0) {
    rotationStartTime = millis();
    countingStarted = true;
    
  }
  patch = patch + 1;

  // Calculate treadmill speed when rotation detected
  if (countingStarted && sumSensorValues > 1 && (millis() - rotationStartTime >= 500)) {
    unsigned long rotationEndTime = millis();
    unsigned long rotationTime = rotationEndTime - rotationStartTime;
    float treadmillSpeed = (trackCircumference / (rotationTime / 1000.0) * 3.6)/2; // Convert milliseconds to seconds

    // Convert speed and angle to strings
    String speedStr = String(treadmillSpeed);
    String angleStr = String(angle);

    // Concatenate speed and angle into one string
    // Concatenate speed and angle into one string
    String data = speedStr + "," + angleStr + ",";

    // Send data over Bluetooth
    ESP_BT.println(data);
    Serial.println(data);
    

    // Reset rotation start time and stop counting
    rotationStartTime = millis();
    countingStarted = false;
  }
    
  // } else {
  //   display.clearDisplay();
  //   display.setCursor(0, 0);
  //   display.println("SmartStride");
  //   display.println("Bluetooth Not Connected");
  //   display.display();
  // }
}
