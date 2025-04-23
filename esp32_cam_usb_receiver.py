import serial
import time
import struct
import numpy as np
import cv2

# --- Serial Port Parameters ---
PORT      = '/dev/ttyUSB0'
BAUDRATE  = 921600
TIMEOUT   = 0.5

# --- Serial Port Setup Function ---
def setup_serial(port, baudrate, timeout):
    ser = serial.Serial()
    ser.port = port
    ser.baudrate = baudrate
    ser.timeout = timeout
    ser.setDTR(False)       # Avoid auto-reset
    ser.setRTS(False)
    ser.open()
    time.sleep(2)           # Allow ESP32-CAM to boot and start streaming
    ser.reset_input_buffer()
    return ser

def refresh_serial(ser):
    print("[*] Manually refreshing serial connection...")
    try:
        ser.close()
        time.sleep(0.5)
        ser.open()
        time.sleep(2)
        ser.reset_input_buffer()
        print("[+] Refresh complete.")
    except Exception as e:
        print(f"[!] Refresh failed: {e}")

# --- Initialize ---
ser = setup_serial(PORT, BAUDRATE, TIMEOUT)
window_name = 'ESP32-CAM Stream'
cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
cv2.resizeWindow(window_name, 640, 480)

try:
    while True:
        # --- Read 4-byte frame length ---
        header = ser.read(4)
        if len(header) == 4:
            frame_len = struct.unpack('<I', header)[0]
            if 0 < frame_len < 500_000:
                data = ser.read(frame_len)
                while len(data) < frame_len:
                    data += ser.read(frame_len - len(data))
                arr = np.frombuffer(data, dtype=np.uint8)
                frame = cv2.imdecode(arr, cv2.IMREAD_COLOR)
                if frame is not None:
                    cv2.imshow(window_name, frame)

        # --- Keyboard input handling ---
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('r'):
            refresh_serial(ser)

        if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
            break

finally:
    ser.close()
    cv2.destroyAllWindows()
