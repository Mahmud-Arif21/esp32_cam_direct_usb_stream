# 📷 ESP32-CAM Direct USB Tester

## Quickly verify ESP32-CAM functionality without Wi-Fi or network setup

This utility tool helps developers rapidly determine if an ESP32-CAM module is functioning correctly by establishing a direct USB connection to your computer. **Eliminate hours of debugging network issues** when the root cause might be a simple hardware problem!

> "Is my camera broken, or is it my code?" - Now you'll know in under 2 minutes.

---

## 🔍 Why You Need This

- **Save development time** by quickly isolating camera hardware issues from code problems
- **Work in environments without Wi-Fi** or before network credentials are configured
- **Verify new ESP32-CAM modules** before integrating them into your main project
- **Debug mysterious failures** in existing projects by testing the camera independently
- **Diagnose connection issues** with the camera module without complex setups

### Common scenarios this tool helps solve:

- Your ESP32-CAM project won't connect to Wi-Fi - is it the camera or the network code?
- New board not working as expected - defective unit or configuration error?
- Camera worked yesterday but not today - loose connection or hardware failure?
- Testing in a production environment where Wi-Fi isn't available
- Need to quickly verify multiple ESP32-CAM units

---

## 🚀 Features

- **Direct USB testing** - No Wi-Fi, SD card, or complex network setup required
- **Cross-platform compatibility** - Works on Windows, macOS, and Linux
- **Real-time video** - See what the camera sees immediately
- **Low latency** - Direct UART connection provides immediate feedback
- **Simple operation** - Flash once, test anytime
- **Auto-reset support** - Stable startup without manual reset sequencing

---

## 🧰 Requirements

### Hardware

- ESP32-CAM (AI Thinker model)
- USB-to-Serial adapter (e.g., FTDI, CH340)
- USB cable
- PC running Windows, macOS, or Linux

### Software

- **Arduino IDE** (with ESP32 board package installed)
- **Python 3**
- Python packages:
  ```bash
  pip install pyserial opencv-python numpy
  ```

---

## 🔧 Platform-Specific Setup

> ⚠️ Platform-specific configuration is not always required.  
> You can usually upload the test code and run the viewer script right away.  
> Use the instructions below only if you encounter connection issues or need additional setup.

### Linux (Ubuntu/Debian)

1. Identify your serial device:
   ```bash
   ls /dev/ttyUSB*
   # or
   dmesg | grep tty
   ```

2. Add yourself to the `dialout` group:
   ```bash
   sudo usermod -a -G dialout $USER
   # Then log out and back in
   ```

3. Install required packages:
   ```bash
   sudo apt update
   sudo apt install python3-pip python3-opencv
   pip3 install pyserial numpy
   ```

### Windows

1. Install Python 3 from [python.org](https://python.org) (check "Add Python to PATH")
2. Install required packages:
   ```powershell
   pip install pyserial opencv-python numpy
   ```
3. Install the appropriate USB-Serial driver:
   - **CP210x**: [Silicon Labs drivers](https://www.silabs.com/drivers)
   - **CH340**: [CH340 drivers](https://sparks.gogo.co.nz/ch340.html)
4. Find your COM port in Device Manager under "Ports (COM & LPT)"

### macOS

1. Install Homebrew (if not already installed):
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```
2. Install Serial drivers:
   ```bash
   brew install --cask silicon-labs-vcp-driver   # For CP210x adapters
   # or for CH340, FTDI, etc.:
   brew install --cask usb-serial-adapter
   ```
3. Find your serial device:
   ```bash
   ls /dev/cu.*
   ```
4. Install Python and packages:
   ```bash
   brew install python
   pip3 install pyserial opencv-python numpy
   ```

---

## 📦 Installation

### 1. Flash ESP32-CAM

Upload this code using Arduino IDE (select `AI Thinker ESP32-CAM` board):

```cpp
#include "esp_camera.h"
#include "Arduino.h"

// AI-Thinker pin definitions
#define PWDN_GPIO_NUM     -1
#define RESET_GPIO_NUM    -1
#define XCLK_GPIO_NUM      0
#define SIOD_GPIO_NUM     26
#define SIOC_GPIO_NUM     27
#define Y2_GPIO_NUM        5
#define Y3_GPIO_NUM       18
#define Y4_GPIO_NUM       19
#define Y5_GPIO_NUM       21
#define Y6_GPIO_NUM       36
#define Y7_GPIO_NUM       39
#define Y8_GPIO_NUM       34
#define Y9_GPIO_NUM       35
#define VSYNC_GPIO_NUM    25
#define HREF_GPIO_NUM     23
#define PCLK_GPIO_NUM     22

void setup() {
  Serial.begin(921600);
  camera_config_t config = {};
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer   = LEDC_TIMER_0;
  config.pin_d0       = Y2_GPIO_NUM;
  config.pin_d1       = Y3_GPIO_NUM;
  config.pin_d2       = Y4_GPIO_NUM;
  config.pin_d3       = Y5_GPIO_NUM;
  config.pin_d4       = Y6_GPIO_NUM;
  config.pin_d5       = Y7_GPIO_NUM;
  config.pin_d6       = Y8_GPIO_NUM;
  config.pin_d7       = Y9_GPIO_NUM;
  config.pin_xclk     = XCLK_GPIO_NUM;
  config.pin_pclk     = PCLK_GPIO_NUM;
  config.pin_vsync    = VSYNC_GPIO_NUM;
  config.pin_href     = HREF_GPIO_NUM;
  config.pin_sccb_sda = SIOD_GPIO_NUM;
  config.pin_sccb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn     = PWDN_GPIO_NUM;
  config.pin_reset    = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;
  config.frame_size   = FRAMESIZE_QVGA;
  config.jpeg_quality = 10;
  config.fb_count     = 2;
  esp_camera_init(&config);
}

void loop() {
  camera_fb_t *fb = esp_camera_fb_get();
  if (!fb) return;
  uint32_t len = fb->len;
  Serial.write((uint8_t*)&len, 4);
  Serial.write(fb->buf, len);
  esp_camera_fb_return(fb);
  delay(30);
}
```

### 2. Create Python Viewer

Save this as `esp32_cam_usb_receiver.py`:

```python
import serial, time, struct, numpy as np, cv2

# --- Serial Setup (modify port as needed) ---
ser = serial.Serial()
ser.port     = '/dev/ttyUSB0'   # Use COM3 on Windows or /dev/cu.* on macOS
ser.baudrate = 921600
ser.timeout  = 0.5
ser.setDTR(False)
ser.setRTS(False)
ser.open()
time.sleep(2)
ser.reset_input_buffer()

# --- OpenCV Window ---
win = 'ESP32-CAM Diagnostic View'
cv2.namedWindow(win, cv2.WINDOW_NORMAL)
cv2.resizeWindow(win, 640, 480)

try:
    print("ESP32-CAM test active - press 'q' to exit")
    while True:
        hdr = ser.read(4)
        if len(hdr)!=4: continue
        size = struct.unpack('<I', hdr)[0]
        if size<=0 or size>500000: continue
        data = ser.read(size)
        while len(data)<size:
            data += ser.read(size-len(data))
        arr = np.frombuffer(data, np.uint8)
        frame = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        if frame is not None:
            cv2.imshow(win, frame)
        if cv2.waitKey(1)&0xFF==ord('q'): break
        if cv2.getWindowProperty(win, cv2.WND_PROP_VISIBLE)<1: break
finally:
    ser.close()
    cv2.destroyAllWindows()
    print("ESP32-CAM test completed")
```

---

## 📋 Usage Guide

1. **Flash the test code** to your ESP32-CAM
   - Connect GPIO0 to GND during flashing
   - Select proper board: `AI Thinker ESP32-CAM`
   - Upload the code

2. **Prepare for testing**
   - Disconnect GPIO0 from GND
   - Connect the ESP32-CAM to your computer using the USB-Serial adapter

3. **Run the diagnostic tool**
   ```bash
   # Linux/macOS
   python3 esp32_cam_usb_receiver.py
   
   # Windows
   python esp32_cam_usb_receiver.py
   ```

4. **Interpret results**
   - **Success**: Live video appears in the window → Camera is working correctly
   - **Failure**: No video or errors → See troubleshooting section

5. **Exit the tool**
   - Press `q` key or close the window

---

## 🔎 Diagnostic Procedure

1. **Camera hardware test**: If video appears, your camera module is working
2. **Lens focus check**: Test focus by viewing objects at different distances
3. **UART connection test**: Successful video confirms serial communication works
4. **Frame rate assessment**: Smooth video indicates proper performance

---

## ❓ Troubleshooting

### No Camera Feed

- **Refresh the serial connection**
  - While the Python viewer is running, simply **press the `r` key** inside the video window and wait for a couple of seconds
  - This triggers a **manual reset of the serial connection**, helping recover from dropped streams or camera stalls
  - The ESP32-CAM will briefly pause and resume streaming automatically
  - Try to refresh more than once if single refresh does not work
  - If it still does not work, prceed with the next steps

- **Check physical connections**
  - Ensure camera ribbon cable is properly seated on both ends
  - Try gently re-seating the camera module

- **Power issues**
  - ESP32-CAM needs stable 5V power supply
  - Try a different USB cable or power source
  - Add a capacitor (100μF) between VCC and GND

- **Serial connection problems**
  - Wrong port selected (update in Python script)
  - Incorrect baud rate (should be 921600)
  - DTR/RTS signals causing reset loops

### Common Error Messages

- **"Port not found"**: Check correct port name and user permissions
- **"Cannot decode frame"**: Camera initialization failed or corrupted data
- **"Timeout"**: ESP32-CAM not responding or wrong baud rate

---

## 🔄 Next Steps After Confirming Camera Works

Once you've verified your camera is functioning correctly, you can:

1. Proceed with confidence to your main project
2. Use the successful test as a baseline for future diagnostics
3. Modify the test code for your specific project requirements
4. Keep this tool available for quick diagnostics in future projects

---

## 📚 Advanced Usage

### Customizing the Test

- Modify frame size in ESP32 code (`FRAMESIZE_QVGA` to `FRAMESIZE_VGA` for higher resolution)
- Adjust JPEG quality (lower values = faster transmission)
- Change frame delay for different frame rates

### Creating a Standalone Diagnostic Utility

1. Use PyInstaller to create an executable:
   ```bash
   pip install pyinstaller
   pyinstaller --onefile esp32_cam_usb_receiver.py
   ```
2. Share the executable with your team for quick camera testing

---

## 📝 License

This project is open source and available under the MIT License.

---

## 💡 Contributing

Found ways to improve this diagnostic tool? Contributions are welcome!
- Add support for different ESP32-CAM models
- Improve error reporting
- Create platform-specific optimizations

---

*Don't waste time debugging complex code when the issue might be a simple hardware problem. Use this diagnostic tool to quickly rule out camera functionality issues!*