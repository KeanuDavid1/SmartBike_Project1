import math
from smbus import SMBus


class Accelerometer:
    def __init__(self, par_i2c_addr, par_reg_pwr_ctl, par_reg_data_format, par_reg_data_start):
        self.i2c_address = par_i2c_addr
        self.reg_pwr_ctl = par_reg_pwr_ctl
        self.reg_data_format = par_reg_data_format
        self.reg_data_start = par_reg_data_start
        self.i2c = SMBus()
        self.i2c.open(1)
        self.i2c.write_byte_data(self.i2c_address, self.reg_pwr_ctl, 0x08)
        self.i2c.write_byte_data(self.i2c_address, self.reg_data_format, 0x0a)
        self.data = self.i2c.read_i2c_block_data(self.i2c_address, self.reg_data_start, 6)

    @staticmethod
    def bits_to_int(val):
        if val >> 15:
            val = ~val + 1
            val = val & 0xffff
            # val = - val
        return val

    def read_data(self, val):
        if val == "x":
            x = self.data[1] << 8 | self.data[0]
            x_int = Accelerometer.bits_to_int(x)
            x_g = x_int * 4 / 1000
            return x_g
        if val == "y":
            y = self.data[3] << 8 | self.data[2]
            y_int = Accelerometer.bits_to_int(y)
            y_g = y_int * 4 / 1000
            return y_g
        if val == "z":
            z = self.data[5] << 8 | self.data[4]
            z_int = Accelerometer.bits_to_int(z)
            z_g = z_int * 4 / 1000
            return z_g

    def get_speed(self):
        # X
        x = self.data[1] << 8 | self.data[0]
        x_int = Accelerometer.bits_to_int(x)
        x_g = x_int * 4 / 1000

        # Y
        y = self.data[3] << 8 | self.data[2]
        y_int = Accelerometer.bits_to_int(y)
        y_g = y_int * 4 / 1000

        # Z
        z = self.data[5] << 8 | self.data[4]
        z_int = Accelerometer.bits_to_int(z)
        z_g = z_int * 4 / 1000

        gravity = math.sqrt(x_g ** 2 + y_g ** 2 + z_g ** 2)
        speed = gravity * 3.6
        return speed
