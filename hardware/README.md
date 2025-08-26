# 🔧 Hardware

This directory contains all hardware-related components for the SmartStride treadmill accessory.

## 📁 Structure

- **`firmware/`** - ESP32 firmware code and Arduino sketches
- **`schematics/`** - Circuit diagrams and wiring schematics (coming soon)

## 🛠️ Components

- **ESP32** - Main microcontroller with Bluetooth capability
- **MPU6050** - 6-axis gyroscope and accelerometer for inclination detection
- **OLED Display** - Real-time status and data visualization
- **LDR Sensors** - Light-dependent resistors for speed detection
- **Custom PCB** - Integrated circuit board design (coming soon)

## 🚀 Quick Start

1. Install Arduino IDE with ESP32 board support
2. Install required libraries (see firmware README)
3. Upload the SmartStrideBLEDevice.ino to your ESP32
4. Connect sensors according to pin configuration

For detailed wiring diagrams and component specifications, see the documentation in `/docs`.
