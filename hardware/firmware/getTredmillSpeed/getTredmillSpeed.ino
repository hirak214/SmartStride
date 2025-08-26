const int sensorPin = 2; // Use the pin where you have one of the sensors
const float metersPerSecond = 0.555556; // Convert speed to meters per second

unsigned long rotationStartTime = 0;
unsigned long lastRotationTime = 0;
bool countingStarted = false;

float trackCircumference = 0.0; // Initialize to 0, will be updated after one rotation

void setup() {
  Serial.begin(115200);
  pinMode(sensorPin, INPUT);
}

void loop() {
  int sensorValue = digitalRead(sensorPin);
  if (sensorValue == 1 && !countingStarted) {
    
    // Record the start time and mark counting as started
    rotationStartTime = millis();
    countingStarted = true;
  
  }
  

  if (countingStarted && (millis() - rotationStartTime >= 1500 && sensorValue == 1)) {

    // Calculate time taken for one rotation
    unsigned long rotationEndTime = millis();
    unsigned long rotationTime = rotationEndTime - rotationStartTime;

    // Print raw sensor values and rotation times for debugging
    Serial.print(", Rotation Time: ");
    Serial.print(rotationTime);
    Serial.println(" milliseconds");

    // Calculate track circumference based on the formula
    trackCircumference = metersPerSecond * (rotationTime / 1000.0); // Convert milliseconds to seconds

    Serial.print("Track Circumference: ");
    Serial.print(trackCircumference);
    Serial.println(" meters");

    // Reset the start time and totalSensorValues for the next rotation
    rotationStartTime = millis();

    // Stop further counting
    countingStarted = false;
  }

  delay(1); // Add a delay to avoid rapid reading
}
