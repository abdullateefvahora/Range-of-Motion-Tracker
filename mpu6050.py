# Save this as mpu6050.py
import math
import time


class MPU6050:
    def __init__(self, i2c, addr=0x68):
        self.i2c = i2c
        self.addr = addr
        self.i2c.writeto_mem(self.addr, 0x6B, b"\x00")  # Wake up MPU6050

    def read_raw(self, reg):
        data = self.i2c.readfrom_mem(self.addr, reg, 2)
        value = int.from_bytes(data, "big")
        if value > 32767:
            value -= 65536
        return value

    def get_accel_data(self):
        ax = self.read_raw(0x3B) / 16384.0
        ay = self.read_raw(0x3D) / 16384.0
        az = self.read_raw(0x3F) / 16384.0
        return {"x": ax, "y": ay, "z": az}
