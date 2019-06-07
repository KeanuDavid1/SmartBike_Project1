import serial


class SerialRaspberry:

    def __init__(self, par_poort, par_baudrate=9600):
        self.__poort = par_poort
        self.__baudrate = par_baudrate

    @property
    def poort(self):
        return self.__poort

    @poort.setter
    def poort(self, value):
        self.__poort = value

    def send_data(self, boodschap):
        ser = serial.Serial(self.__poort)
        ser.write(boodschap)
        ser.close()

    def read_data(self):
        with serial.Serial(self.__poort) as ser:
            reply = ser.readline()
            return reply
