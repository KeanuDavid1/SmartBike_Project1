import spidev

spi = spidev.SpiDev()


class mcp3008:

    def __init__(self, par_bytes_in=0, par_clockspeed=(10 ** 5)):
        self.__bytes_in = par_bytes_in
        self.__clockspeed = par_clockspeed

    @property
    def bytes_in(self):
        return self.__bytes_in

    @bytes_in.setter
    def bytes_in(self, value):
        self.__bytes_in = value

    @property
    def clockspeed(self):
        return self.__clockspeed

    @clockspeed.setter
    def clockspeed(self, value):
        self.__clockspeed = value

    def read_data_ldr(self, byte_data):
        spi.open(0, 0)
        spi.max_speed_hz = self.__clockspeed
        bytes_in = spi.xfer2([0b00000001, byte_data, 0])
        spi.close()

        # y-waarde bytes

        byte1 = bytes_in[1]
        byte2 = bytes_in[2]
        bit_waarde = byte1 << 8 | byte2

        ldr_waarde = (bit_waarde / 1023) * 100
        ldr_waarde_omrekenen = 100 - ldr_waarde

        return ldr_waarde_omrekenen
