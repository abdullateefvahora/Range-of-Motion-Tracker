import network
import socket
import time
import math
from machine import Pin, I2C
from mpu6050 import MPU6050
from wifi_secrets import ssid, password

# Setup Wi-Fi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)

print("Connecting to Wi-Fi...", end="")
while not wlan.isconnected():
    print(".", end="")
    time.sleep(0.5)
print("\nConnected to", ssid)
print("IP:", wlan.ifconfig()[0])

# Setup I2C for both sensors
i2c0 = I2C(0, scl=Pin(1), sda=Pin(0))  # Thigh
i2c1 = I2C(1, scl=Pin(3), sda=Pin(2))  # Shin

sensor_thigh = MPU6050(i2c0, addr=0x68)
sensor_shin = MPU6050(i2c1, addr=0x68)


def get_pitch(ax, ay, az):
    return math.degrees(math.atan2(ax, math.sqrt(ay**2 + az**2)))


def read_flexion():
    ax1, ay1, az1 = sensor_thigh.get_accel()
    ax2, ay2, az2 = sensor_shin.get_accel()
    pitch1 = get_pitch(ax1, ay1, az1)
    pitch2 = get_pitch(ax2, ay2, az2)
    return round(pitch1, 0), round(pitch2, 0), round(abs(pitch1 - pitch2), 0)


# Setup HTTP server
addr = socket.getaddrinfo("0.0.0.0", 80)[0][-1]
s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(addr)
s.listen(1)

print("Listening on", addr)

html = """<!DOCTYPE html>
<html>
<head><title>Knee Flexion</title></head>
<body style="font-family:sans-serif;">
  <h2>Knee Flexion Angle</h2>
  <p>Thigh: <b>{}</b> degrees</p>
  <p>Shin: <b>{}</b> degrees</p>
  <p style="font-size: 24px;">Flexion: <b>{}</b> degrees</p>
  <meta http-equiv="refresh" content="1">
</body>
</html>"""

# Main server loop
while True:
    try:
        cl, addr = s.accept()
        request = cl.recv(1024)
        pitch1, pitch2, flexion = read_flexion()
        response = html.format(pitch1, pitch2, flexion)
        cl.send("HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n")
        cl.send(response)
        cl.close()
    except Exception as e:
        print("Error:", e)
        time.sleep(1)
