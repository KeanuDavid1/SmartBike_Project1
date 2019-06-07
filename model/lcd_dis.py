import time

from RPi import GPIO


class lcd:

    def __init__(self, D0=18, D1=24, D2=25, D3=19, D4=13, D5=6, D6=5, D7=22, rs=20, E=21):
        self.__arrPort = [D0, D1, D2, D3, D4, D5, D6, D7]
        self.__rswaarde = rs
        self.__Ewaarde = E
        self.setup()
        self.init_LCD()

    @property
    def arrPort(self):
        return self.__arrPort

    @property
    def rswaarde(self):
        return self.__rswaarde

    @property
    def ewaarde(self):
        return self.__Ewaarde

    def init_LCD(self):
        self.send_instruction(0b00111000)
        self.send_instruction(0b00001111)
        self.send_instruction(0b00000001)

    def set_data_bits(self, byte):
        for i in range(8):
            bit = (byte >> i) & 1
            GPIO.output(self.arrPort[i], bit)

    def send_instruction(self, value):
        GPIO.output(self.ewaarde, GPIO.HIGH)
        GPIO.output(self.rswaarde, GPIO.LOW)
        self.set_data_bits(value)
        GPIO.output(self.ewaarde, GPIO.LOW)
        time.sleep(0.01)

    def send_character(self, value):
        GPIO.output(self.ewaarde, 1)
        GPIO.output(self.rswaarde, 1)
        self.set_data_bits(value)
        GPIO.output(self.ewaarde, 0)
        time.sleep(0.01)

    def second_row(self):
        self.send_instruction(0b11000000)

    def send_message(self, value):
        teller = 0
        for i in value:
            self.send_character(ord(i))
            teller += 1
            if teller >= 16:
                self.send_character(ord(i))
                teller += 1
            if teller == 24:
                self.send_instruction(0b00000001)
                self.send_character(ord(i))
                teller += 1

    def setup(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.rswaarde, GPIO.OUT)
        GPIO.setup(self.ewaarde, GPIO.OUT)
        GPIO.setup(self.arrPort, GPIO.OUT)
