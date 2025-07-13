# 🦵 Pico-W Knee Flexion Tracker

A simple IoT device built with a Raspberry Pi Pico W and two MPU-6050 sensors to measure, track, and guide knee range of motion exercises in real-time. The data is displayed on a self-hosted web page accessible from any device on the local network.

This project is ideal for individuals recovering from knee surgery (such as an ACL reconstruction) who need to monitor their flexion progress and meet specific physiotherapy targets.

-----

## Features

  * **Live Angle Display:** Real-time feedback on your current knee flexion.
  * **Max Flexion Tracking:** Records the peak angle achieved per session.
  * **Adjustable Goals:** Set custom targets for both flexion angle and hold time.
  * **Automatic Hold Timer:** Tracks time spent at your target angle and provides visual feedback in the form of background changes

-----

## How It Works

The system uses two MPU-6050 accelerometer/gyroscope modules to determine the knee angle.

  * **Hardware:** One sensor is strapped to the thigh and the other to the shin. The Raspberry Pi Pico W reads data from both sensors, runs the calculations, and hosts the web server.
  * **Software:** The core logic runs in MicroPython on the Pico. It reads the 3D acceleration vector from each sensor.
    Using vector math (specifically the dot product), it calculates the precise angle between the two sensors.
    This method is powerful because it works regardless of whether you are standing, sitting, or lying down.
    The Pico then serves an HTML page that displays this data and sends commands back to the device.

-----

## Setup & Installation

### Required Hardware

  * 1 x Raspberry Pi Pico W
  * 2 x MPU-6050 Gyro/Accelerometer modules
  * Jumper Wires (or a custom soldered board)
  * Power source for the Pico (e.g., USB power bank)
  * Straps to attach sensors to your leg

### Wiring

This project uses two separate I2C buses. Connect the sensors directly to the Pico's pins as shown below.

| Sensor | Sensor Pin | Pico W Pin | Pico Physical Pin |
| :--- | :--- | :--- | :--- |
| **Thigh Sensor** | `VCC` | 3V3 (OUT) | 36 |
| | `GND` | GND | 38 |
| | `SDA` | **GP0** | 1 |
| | `SCL` | **GP1** | 2 |
| **Shin Sensor** | `VCC` | 3V3 (OUT) | 36 (Shared) |
| | `GND` | GND | 33 |
| | `SDA` | **GP2** | 4 |
| | `SCL` | **GP3** | 5 |

### Configuration & Running

1. If you haven't already, flash MicroPython onto your Raspberry Pi Pico W, and upload this repository's files to the root directory of your Pico W.
   
2.  **Configure Wi-Fi:** Create a file named `wifi_secrets.py` in the root directory of your Pico. Add your Wi-Fi network name and password to this file.

    ```python
    # wifi_secrets.py
    ssid = "YOUR_WIFI_NAME"
    password = "YOUR_WIFI_PASSWORD"
    ```

3.  **Run the Project:** With all the project files loaded on the Pico, run `main.py` using your preferred MicroPython IDE (like Thonny). The console will display the IP address once it connects to your network.
