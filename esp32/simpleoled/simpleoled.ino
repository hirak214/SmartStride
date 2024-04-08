#include <Wire.h>  // Include Wire Library for I2C
#include <Adafruit_GFX.h>  // Include Adafruit Graphics Library
#include <Adafruit_SSD1306.h>  // Include Adafruit OLED Library

#define SCREEN_WIDTH 128  // OLED display width, in pixels
#define SCREEN_HEIGHT 64  // OLED display height, in pixels
#define OLED_RESET    -1  // Reset pin # (or -1 if sharing Arduino reset pin)

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET); // Initialize Adafruit SSD1306 display library

void setup() {
  Serial.begin(115200);

  if(!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) { // Address 0x3C for 128x64
    Serial.println(F("SSD1306 allocation failed"));
    for(;;);
  }
  
  display.display();  // Display setup
  delay(2000);  // Pause for 2 seconds
  display.clearDisplay(); // Clear the buffer
}

void loop() {
  display.setTextSize(2);      // Increase font size
  display.setTextColor(SSD1306_WHITE); // Draw white text
  
  // Calculate the starting position to center the text
  int16_t x = (SCREEN_WIDTH - display.getCursorX()) / 2;
  int16_t y = (SCREEN_HEIGHT - display.getCursorY()) / 2;
  
  display.setCursor(x, y);     // Set cursor to center align the text
  display.println(F("Happy Birthday")); // Print "Happy Birthday"
  display.println(F("YASHVI <2")); // Print "YASHVI <2"
  display.display(); // Display
  delay(2000); // Pause for 2 seconds
  display.clearDisplay(); // Clear the buffer
}
