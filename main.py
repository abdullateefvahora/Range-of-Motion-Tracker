import network
import socket
import time
import math
from machine import Pin, I2C
from mpu6050 import MPU6050
from secrets import ssid, password

# Connect to Wi-Fi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)
print("Connecting to Wi-Fi...", end="")
while not wlan.isconnected():
    print(".", end="")
    time.sleep(0.5)
print("\nConnected. IP:", wlan.ifconfig()[0])

# Setup I2C buses and sensors
i2c0 = I2C(0, scl=Pin(1), sda=Pin(0))  # Thigh sensor
i2c1 = I2C(1, scl=Pin(3), sda=Pin(2))  # Shin sensor

sensor_thigh = MPU6050(i2c0, addr=0x68)
sensor_shin = MPU6050(i2c1, addr=0x68)


# --- Helper Functions for Angle Between Y-Z Projections ---
def dot_2d(a, b):
    return a[0] * b[0] + a[1] * b[1]


def magnitude_2d(v):
    return math.sqrt(v[0] ** 2 + v[1] ** 2)


def angle_between_yz(a1, a2):
    """Calculate angle between two 2D vectors (ay, az) from each sensor."""
    vec1 = (a1[1], a1[2])  # (ay, az)
    vec2 = (a2[1], a2[2])  # (ay, az)

    mag1 = magnitude_2d(vec1)
    mag2 = magnitude_2d(vec2)
    if mag1 == 0 or mag2 == 0:
        return 0.0

    cos_angle = dot_2d(vec1, vec2) / (mag1 * mag2)
    cos_angle = max(-1.0, min(1.0, cos_angle))  # Clamp to avoid math domain error
    return math.degrees(math.acos(cos_angle))


def read_flexion():
    a1 = sensor_thigh.get_accel()
    a2 = sensor_shin.get_accel()

    thigh_pitch = math.degrees(math.atan2(a1[1], a1[2]))
    shin_pitch = math.degrees(math.atan2(a2[1], a2[2]))
    flexion_angle = angle_between_yz(a1, a2)

    return round(thigh_pitch), round(shin_pitch), round(flexion_angle)


# --- Start Web Server ---
addr = socket.getaddrinfo("0.0.0.0", 80)[0][-1]
s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(addr)
s.listen(1)
print("Web server running on http://{}".format(wlan.ifconfig()[0]))

max_flexion = 0

while True:
    try:
        cl, addr = s.accept()
        request = cl.recv(1024)

        thigh, shin, flexion = read_flexion()

        if flexion > max_flexion:
            max_flexion = flexion

        # --- HTML Template ---
        response = f"""<!DOCTYPE html>
        <html>
        <head><title>Knee Flexion</title></head>
        <body style="font-family: sans-serif; text-align: center; margin-top: 50px;">
          <h2>Knee Flexion Measurement</h2>
          <p style="font-size: 24px;">Flexion Angle: <b>{flexion}&deg</b></p>
          <p style="font-size: 24px;">Max Flexion: <b>{max_flexion}&deg</b></p>
          <meta http-equiv="refresh" content="0.5">
        </body>
        </html>"""

        cl.send("HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n")
        cl.send(response)
        cl.close()
    except Exception as e:
        print("Error:", e)
        time.sleep(1)
