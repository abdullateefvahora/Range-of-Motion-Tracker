from time import sleep


class MPU6050:
    def __init__(self, i2c, addr=0x68):
        self.i2c = i2c
        self.addr = addr
        # Wake up the MPU-6050 as it starts in sleep mode
        self.i2c.writeto_mem(self.addr, 0x6B, b"\x00")

    def read_raw_data(self, reg):
        data = self.i2c.readfrom_mem(self.addr, reg, 2)
        value = data[0] << 8 | data[1]
        if value > 32767:
            value -= 65536
        return value

    def get_accel(self):
        ax = self.read_raw_data(0x3B) / 16384.0
        ay = self.read_raw_data(0x3D) / 16384.0
        az = self.read_raw_data(0x3F) / 16384.0
        return ax, ay, az

    def get_gyro(self):
        gx = self.read_raw_data(0x43) / 131.0
        gy = self.read_raw_data(0x45) / 131.0
        gz = self.read_raw_data(0x47) / 131.0
        return gx, gy, gz
