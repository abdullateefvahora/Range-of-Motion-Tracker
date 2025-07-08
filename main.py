import network
import socket
import time
import utime
import math
import ure
from machine import Pin, I2C
from mpu6050 import MPU6050
from wifi_secrets import ssid, password

max_flexion = 0
hold_start_time = None
target_hold_secs = 5
target_flexion = 120

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
i2c_thigh = I2C(0, scl=Pin(1), sda=Pin(0))
i2c_shin = I2C(1, scl=Pin(3), sda=Pin(2))

sensor_thigh = MPU6050(i2c_thigh, addr=0x68)
sensor_shin = MPU6050(i2c_shin, addr=0x68)


# --- Helper Functions for Angle Between Y-Z Axis ---
def dot_2d(a, b):
    return a[0] * b[0] + a[1] * b[1]


def magnitude_2d(v):
    return math.sqrt(v[0] ** 2 + v[1] ** 2)


def angle_between_yz(a1, a2):
    vec1 = (a1[1], a1[2])  # (ay, az)
    vec2 = (a2[1], a2[2])  # (ay, az)

    mag1 = magnitude_2d(vec1)
    mag2 = magnitude_2d(vec2)
    if mag1 == 0 or mag2 == 0:
        return 0.0

    cos_angle = dot_2d(vec1, vec2) / (mag1 * mag2)
    cos_angle = max(-1.0, min(1.0, cos_angle))  # Edge case
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


while True:
    try:
        cl, addr = s.accept()
        request = cl.recv(1024).decode()

        match_flex = ure.search(r"adjust_flexion=(-?\d+)", request)
        match_hold = ure.search(r"adjust_hold=(-?\d+)", request)

        if "/?reset=1" in request:
            max_flexion = 0
            cl.send("HTTP/1.1 302 Found\r\nLocation: /\r\n\r\n")
            cl.close()
            continue
        elif match_flex:
            target_flexion += int(match_flex.group(1))
            target_flexion = max(0, min(180, target_flexion))
            match_flex = None
            cl.send("HTTP/1.1 302 Found\r\nLocation: /\r\n\r\n")
            cl.close()
            continue
        elif match_hold:
            target_hold_secs += int(match_hold.group(1))
            target_hold_secs = max(5, min(30, target_hold_secs))
            match_hold = None
            cl.send("HTTP/1.1 302 Found\r\nLocation: /\r\n\r\n")
            cl.close()
            continue
        else:
            thigh, shin, flexion = read_flexion()

            if flexion > max_flexion:
                max_flexion = flexion

            # Timer logic
            holding = False
            hold_elapsed = 0
            target_reached = False

            if flexion >= target_flexion:
                if hold_start_time is None:
                    hold_start_time = utime.ticks_ms()
                else:
                    hold_elapsed = (
                        utime.ticks_diff(utime.ticks_ms(), hold_start_time) / 1000
                    )
                    if hold_elapsed >= target_hold_secs:
                        target_reached = True
                        holding = False
                    else:
                        holding = True
            else:
                hold_start_time = None  # Reset timer

        # --- HTML Template ---
        bg_color = "#fff"
        msg = ""

        if target_reached:
            bg_color = "#c3f7c0"  # Light green
            msg = "<h2>Target Reached!</h2>"
        elif holding:
            bg_color = "#f7f7c0"  # Light yellow
            time_left = round(target_hold_secs - hold_elapsed, 1)
            msg = f"<h2>Hold steady! {time_left}s remaining</h2>"

        response = f"""<!DOCTYPE html>
        <html>
        <head><title>Range of Motion</title></head>
        <body style="font-family: sans-serif; background-color:{bg_color}; text-align: center; margin-top: 50px;">
          <h2>Range of Motion Measurement</h2>
          <p style="font-size: 24px;">Flexion Angle: <b>{flexion}&deg</b></p>
          <p style="font-size: 24px;">Max Flexion: <b>{max_flexion}&deg</b></p>
          <form action="/" method="get">
            <button name="reset" value="1" type="submit">Reset Max</button>
          </form>
          <p>Target: <b>{target_flexion}&deg</b>
            <a href="/?adjust_flexion=-2"><button>-2</button></a>
            <a href="/?adjust_flexion=2"><button>+2</button></a>
          </p>

          <p>Hold: <b>{target_hold_secs}s</b>
            <a href="/?adjust_hold=-5"><button>-5s</button></a>
            <a href="/?adjust_hold=5"><button>+5s</button></a>
          </p>
          <meta http-equiv="refresh" content="0.5">
        </body>
        </html>"""

        cl.send("HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n")
        cl.send(response)
        cl.close()
    except Exception as e:
        print("Error:", e)
        time.sleep(1)
