# 🚀 Getting Started with SmartStride

Welcome to SmartStride! This guide will help you set up your AI-powered treadmill accessory from hardware assembly to software configuration.

## 📋 What You'll Need

### Hardware Components
- [ ] **ESP32 Development Board** (ESP32-WROOM-32)
- [ ] **MPU6050 Gyroscope Module** (6-axis accelerometer/gyroscope)
- [ ] **OLED Display** (128x64, I2C interface)
- [ ] **LDR Sensors** (5x light-dependent resistors)
- [ ] **Resistors** (5x 10kΩ for LDR pull-down)
- [ ] **Breadboard or PCB** for connections
- [ ] **Jumper Wires** (male-to-male, male-to-female)
- [ ] **3D Printed Case** (STL files in `/media/renders/`)

### Software Requirements
- [ ] **Arduino IDE** (1.8.19 or later)
- [ ] **Python** (3.8 or later)
- [ ] **PostgreSQL** (12 or later)
- [ ] **Git** for version control

### Tools
- [ ] **Soldering Iron** (optional, for permanent connections)
- [ ] **3D Printer** (for custom case)
- [ ] **Multimeter** (for debugging)

## 🔧 Step 1: Hardware Assembly

### 1.1 Pin Connections

| Component | ESP32 Pin | Notes |
|-----------|-----------|-------|
| **MPU6050** | | |
| VCC | 3.3V | Power supply |
| GND | GND | Ground |
| SDA | GPIO 21 | I2C data |
| SCL | GPIO 22 | I2C clock |
| **OLED Display** | | |
| VCC | 3.3V | Power supply |
| GND | GND | Ground |
| SDA | GPIO 21 | I2C data (shared) |
| SCL | GPIO 22 | I2C clock (shared) |
| **LDR Sensors** | | |
| LDR 1 | GPIO 15 | With 10kΩ pull-down |
| LDR 2 | GPIO 2 | With 10kΩ pull-down |
| LDR 3 | GPIO 4 | With 10kΩ pull-down |
| LDR 4 | GPIO 18 | With 10kΩ pull-down |
| LDR 5 | GPIO 19 | With 10kΩ pull-down |

### 1.2 Wiring Diagram

```
ESP32                    MPU6050
┌─────────────────┐     ┌─────────┐
│             3.3V├─────┤VCC      │
│              GND├─────┤GND      │
│         GPIO 21 ├─────┤SDA      │
│         GPIO 22 ├─────┤SCL      │
└─────────────────┘     └─────────┘

ESP32                    OLED Display
┌─────────────────┐     ┌─────────┐
│             3.3V├─────┤VCC      │
│              GND├─────┤GND      │
│         GPIO 21 ├─────┤SDA      │
│         GPIO 22 ├─────┤SCL      │
└─────────────────┘     └─────────┘

ESP32                    LDR Sensors
┌─────────────────┐     
│         GPIO 15 ├─────[LDR1]─────┤3.3V
│         GPIO 2  ├─────[LDR2]─────┤3.3V
│         GPIO 4  ├─────[LDR3]─────┤3.3V
│         GPIO 18 ├─────[LDR4]─────┤3.3V
│         GPIO 19 ├─────[LDR5]─────┤3.3V
│              GND├─────[10kΩ]─────┘
└─────────────────┘
```

### 1.3 Assembly Tips
- **Double-check connections** before powering on
- **Use breadboard** for initial testing
- **Secure mounting** of sensors for accurate readings
- **Test each component** individually before final assembly

## 💻 Step 2: Software Setup

### 2.1 Arduino IDE Configuration

1. **Install ESP32 Board Support**
   ```
   File → Preferences → Additional Board Manager URLs
   Add: https://dl.espressif.com/dl/package_esp32_index.json
   ```

2. **Install Required Libraries**
   ```
   Tools → Manage Libraries → Search and Install:
   - Adafruit MPU6050
   - Adafruit SSD1306
   - Adafruit Unified Sensor
   - BluetoothSerial (built-in)
   ```

3. **Board Configuration**
   ```
   Tools → Board → ESP32 Arduino → ESP32 Dev Module
   Tools → Upload Speed → 115200
   Tools → CPU Frequency → 240MHz (WiFi/BT)
   ```

### 2.2 Upload Firmware

1. **Clone Repository**
   ```bash
   git clone https://github.com/hirak214/SmartStride.git
   cd SmartStride
   ```

2. **Open Firmware**
   ```
   Arduino IDE → File → Open
   Navigate to: hardware/firmware/SmartStrideBLEDevice/SmartStrideBLEDevice.ino
   ```

3. **Upload Code**
   ```
   Connect ESP32 via USB
   Select correct COM port in Tools → Port
   Click Upload button (→)
   ```

### 2.3 Verify Hardware

After uploading, your device should:
- [ ] Display "SmartStride" on OLED screen
- [ ] Show "Bluetooth Not Connected" initially
- [ ] LED indicator on ESP32 should blink
- [ ] Serial monitor shows sensor readings at 115200 baud

## 🖥️ Step 3: Backend Setup

### 3.1 Python Environment

1. **Create Virtual Environment**
   ```bash
   cd software/backend
   python -m venv smartstride_env
   
   # Windows
   smartstride_env\Scripts\activate
   
   # macOS/Linux
   source smartstride_env/bin/activate
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

### 3.2 Database Setup

1. **Install PostgreSQL**
   ```bash
   # Ubuntu/Debian
   sudo apt-get install postgresql postgresql-contrib
   
   # macOS (with Homebrew)
   brew install postgresql
   
   # Windows
   # Download from https://www.postgresql.org/download/
   ```

2. **Create Database**
   ```sql
   -- Connect to PostgreSQL
   psql -U postgres
   
   -- Create database and user
   CREATE DATABASE smartstride_db;
   CREATE USER smartstride_user WITH PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE smartstride_db TO smartstride_user;
   ```

3. **Configure Connection**
   ```python
   # Edit software/backend/main.py
   db_params = {
       'dbname': 'smartstride_db',
       'user': 'smartstride_user',
       'password': 'your_password',
       'host': 'localhost',
       'port': '5432'
   }
   ```

### 3.3 Start API Server

```bash
cd software/backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Verify Setup:**
- API Documentation: http://localhost:8000/docs
- Interactive API: http://localhost:8000/redoc
- Health Check: http://localhost:8000/get_run_data/

## 📱 Step 4: Mobile Connection

### 4.1 Bluetooth Pairing

1. **Enable Bluetooth** on your mobile device
2. **Scan for devices** - look for "SmartStride_BT"
3. **Pair device** (no PIN required)
4. **Verify connection** - OLED should show "Bluetooth Connected"

### 4.2 Test Data Transmission

1. **Start treadmill** at low speed
2. **Check serial monitor** for data output:
   ```
   5.2,2.1,
   5.4,2.3,
   5.1,2.0,
   ```
3. **Verify API reception** at `/insert_run_data/` endpoint

## 🧪 Step 5: Testing & Calibration

### 5.1 Sensor Calibration

1. **Speed Calibration**
   ```cpp
   // Adjust in firmware if needed
   float trackCircumference = 3.31; // meters
   ```

2. **Inclination Calibration**
   ```cpp
   // Place device on level surface
   // Record baseline angle reading
   // Adjust offset in code if necessary
   ```

### 5.2 Functional Tests

- [ ] **Speed Detection**: Verify accurate speed readings
- [ ] **Inclination Measurement**: Test with manual treadmill adjustment
- [ ] **Bluetooth Connectivity**: Ensure stable connection
- [ ] **Data Persistence**: Check database storage
- [ ] **API Responses**: Verify all endpoints work correctly

## 🎯 Step 6: First Workout

### 6.1 User Registration

1. **Create Account** via API:
   ```bash
   curl -X POST "http://localhost:8000/signup/" \
        -d "userName:testuser,email:test@example.com,password:securepass"
   ```

2. **Complete Profile**:
   ```bash
   curl -X POST "http://localhost:8000/signup_userdata/" \
        -d "userName:testuser,fullName:Test User,dob:1995-01-01,height:175,weight:70,med:none,gender:M,blood:O+"
   ```

### 6.2 Set Fitness Goals

```bash
curl -X POST "http://localhost:8000/set_goal/" \
     -d "userName:testuser,program:Weight Loss,goal:5,days:30"
```

### 6.3 Start Your First Workout

1. **Mount SmartStride** on your treadmill
2. **Power on device** and verify Bluetooth connection
3. **Start treadmill** at comfortable pace
4. **Monitor real-time data** through API or future mobile app
5. **Let AI adapt** your workout based on performance

## 🔧 Troubleshooting

### Common Issues

**Device won't connect:**
- Check Bluetooth is enabled
- Verify device is powered on
- Try restarting both devices

**Inaccurate readings:**
- Calibrate sensors
- Check sensor placement
- Verify wiring connections

**API errors:**
- Check database connection
- Verify Python dependencies
- Review server logs

**Build failures:**
- Update Arduino libraries
- Check board selection
- Verify USB connection

### Getting Help

- 📚 **Documentation**: Check `/docs` folder
- 🐛 **Issues**: [GitHub Issues](https://github.com/hirak214/SmartStride/issues)
- 💬 **Community**: [GitHub Discussions](https://github.com/hirak214/SmartStride/discussions)
- 📧 **Contact**: hirak.desai@example.com

## 🎉 Next Steps

Congratulations! Your SmartStride is now set up and ready to transform your treadmill workouts. 

**What's next?**
- Explore the AI workout recommendations
- Track your progress over time
- Join the community and share your experience
- Contribute to the project development

Happy running! 🏃‍♂️💨
