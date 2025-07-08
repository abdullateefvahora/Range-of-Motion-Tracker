# --- Helper Functions for Angle Between Y-Z Axis ---
import math 

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


def compute_flexion(sensor_thigh, sensor_shin):
    a1 = sensor_thigh.get_accel()
    a2 = sensor_shin.get_accel()

    thigh_pitch = math.degrees(math.atan2(a1[1], a1[2]))
    shin_pitch = math.degrees(math.atan2(a2[1], a2[2]))
    flexion_angle = angle_between_yz(a1, a2)

    return round(thigh_pitch), round(shin_pitch), round(flexion_angle)
