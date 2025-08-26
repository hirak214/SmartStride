# 🎛️ ESP32 Firmware

Arduino sketches and firmware for the SmartStride IoT device.

## 📋 Required Libraries

```cpp
#include <Adafruit_MPU6050.h>
#include <Adafruit_SSD1306.h>
#include <Adafruit_Sensor.h>
#include "BluetoothSerial.h"
```

## 🔌 Pin Configuration

| Component | Pin |
|-----------|-----|
| LDR Sensors | 15, 2, 4, 18, 19 |
| OLED Display | I2C (SDA: 21, SCL: 22) |
| MPU6050 | I2C (SDA: 21, SCL: 22) |

## 📡 Bluetooth Protocol

The device broadcasts data in the format: `speed,inclination,`

- **Speed**: km/h calculated from treadmill rotation
- **Inclination**: degrees from MPU6050 gyroscope

## 🔧 Firmware Files

- **`SmartStrideBLEDevice.ino`** - Main firmware with full functionality
- **`getTredmillSpeed.ino`** - Speed detection only
- **`simpleoled.ino`** - OLED display testing
- **`Speed.ino`** - Basic speed calculation
- **`bt app sample/`** - Bluetooth testing and mobile app samples
