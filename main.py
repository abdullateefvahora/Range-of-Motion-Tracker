import network
import socket
from machine import Pin, I2C
from mpu6050 import MPU6050
import time
import math

# Wi-Fi credentials
ssid = 'vahora'
password = 'vahora123'

# Connect to Wi-Fi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)

print("Connecting to Wi-Fi...", end="")
while not wlan.isconnected():
    time.sleep(0.5)
    print(".", end="")
print("\nConnected!")
ip = wlan.ifconfig()[0]
print("Visit http://" + ip)

# Set up sensor
i2c = I2C(0, scl=Pin(1), sda=Pin(0))
sensor = MPU6050(i2c)

def get_knee_angle():
    accel = sensor.get_accel_data()
    ax, ay, az = accel['x'], accel['y'], accel['z']
    g = math.sqrt(ax**2 + ay**2 + az**2)
    if g == 0:
        return 0
    ay_norm = ay / g
    ay_norm = max(-1.0, min(1.0, ay_norm))
    angle = math.degrees(math.acos(ay_norm))
    return round(angle, 2)

# Web server setup
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
s = socket.socket()
s.bind(addr)
s.listen(1)

print("Web server running!")

# Serve web page
while True:
    try:
        cl, addr = s.accept()
        request = cl.recv(1024)
        angle = get_knee_angle()
        html = f"""<!DOCTYPE html>
<html><head><title>Knee Angle</title>
<meta http-equiv="refresh" content="1">
</head><body>
<h1>Knee Flexion Angle</h1>
<p><strong>{angle}</strong> degrees</p>
</body></html>"""
        cl.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
        cl.send(html)
        cl.close()
    except Exception as e:
        print("Error:", e)
