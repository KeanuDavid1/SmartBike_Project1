import time
from RPi import GPIO
from flask import Flask, jsonify, request, redirect
# https://flask-socketio.readthedocs.io/en/latest/
from flask_socketio import SocketIO
from flask_cors import CORS
from helpers.Database import Database
from model.lcd_dis import lcd
from subprocess import check_output
from model.analoge_ingang import mcp3008
from model.accelerometer import Accelerometer
import pynmea2
import serial
import threading

# server
app = Flask(__name__)
CORS(app)
socketio = SocketIO(app)
SESSION_TYPE = 'redis'

# modules / classes
conn = Database(app=app, user='mctkeanu', password='mctkeanu147963$$0', db='smartbike_db')
lcd = lcd()
adc = mcp3008()
# acc = Accelerometer(0x53, 0x2D, 0x31, 0x32)

# extra
ips = check_output(['hostname', '--all-ip-addresses'])
lcd.send_message(str(ips).split(' ')[0].lstrip("\\b\'"))
print(ips)

# python3.5 /home/keanu/tmp/pycharm_project_301/app.py

led_voor = 27
led_achter = 17

current_user = "0"
logged_in_users = {}


def setup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(led_voor, GPIO.OUT)
    GPIO.setup(led_achter, GPIO.OUT)


def get_value_ldr():
    status = 0
    licht_waarde = adc.read_data_ldr(0b10000000)
    if licht_waarde < 50:
        status = 1
    else:
        status = 0
    if status == 1:
        conn.set_data("INSERT into datahistory "
                      "VALUES (null, null, %s, (select rfid from user where RFID like %s), %s)",
                      ["ON", current_user, "5"])
    else:
        conn.set_data("INSERT into datahistory "
                      "VALUES (null, null, %s, (select rfid from user where RFID like %s), %s)",
                      ["OFF", current_user, "5"])
    while True:
        status = 0
        licht_waarde = adc.read_data_ldr(0b10000000)
        # print("Licht waarde: %s" % licht_waarde)
        if licht_waarde < 50:
            status = 1
        else:
            status = 0

        if status == 1 and GPIO.input(led_voor) == 0:
            GPIO.output(led_voor, GPIO.HIGH)
            GPIO.output(led_achter, GPIO.HIGH)
            socketio.emit("data", "led aan")
            conn.set_data("INSERT into datahistory "
                          "VALUES (null, null, %s, (select rfid from user where RFID like %s), %s)",
                          ["ON", current_user, "5"])
        elif status == 0 and GPIO.input(led_voor) == 1:
            GPIO.output(led_voor, GPIO.LOW)
            GPIO.output(led_achter, GPIO.LOW)
            socketio.emit("data", "led uit")
            conn.set_data("INSERT into datahistory "
                          "VALUES (null, null, %s, (select rfid from user where RFID like %s), %s)",
                          ["OFF", current_user, "5"])

        # print(acc.get_speed())
        time.sleep(5)


def get_gps_values():
    with serial.Serial('/dev/ttyS0', 9600, timeout=1) as ser:
        while True:
            line = ser.readline()
            # print("Getting GPS values...")
            # print("Recieved GPS data: %s" % line)
            if str(line).find('GPGGA') != -1:
                msg = pynmea2.parse(str(line).lstrip('b\'').rstrip('\\r\\n\''))
                print(msg)
                valueX = msg.latitude
                valueY = msg.longitude
                print("Current location: {0}°, {1}°".format(valueY, valueX))
                conn.set_data('Insert into datahistory '
                              'values (null, null, %s, (select rfid from user where RFID like %s), '
                              '(select idSensoren from sensoren where idSensoren like %s))',
                              [valueX, current_user, 2])
                conn.set_data('Insert into datahistory '
                              'values (null, null, %s, (select rfid from user where RFID like %s), '
                              '(select idSensoren from sensoren where idSensoren like %s))',
                              [valueY, current_user, 2])
            elif str(line).find('GPVTG') != -1 and str(line).find('K') != -1:
                msg = str(line).lstrip('b\'').rstrip('\\r\\n\'')
                print(msg)
                # print(str(msg[msg.find('N') + 2:msg.find('K')]))
                conn.set_data('Insert into datahistory '
                              'values (null, null, %s, (select rfid from user where RFID like %s), '
                              '(select idSensoren from sensoren where idSensoren like %s))',
                              [str(msg[msg.find('N') + 2:msg.find('K')]).rstrip(','), current_user, 3])
            time.sleep(5)


def get_rfid_tag():
    with serial.Serial('/dev/ttyACM0', 9600, timeout=1) as ser:
        while True:
            line = ser.readline()
            code = str(line).lstrip("b\'").lstrip(" ").rstrip("\\r\\n\'")
            if code != "":
                global current_user
                if code != current_user and current_user != "0":
                    print("User OUT")
                    conn.set_data('Insert into datahistory '
                                  'values (null, null, %s, (select rfid from user where RFID like %s), '
                                  '(select idSensoren from sensoren where idSensoren like %s))',
                                  ["OUT", current_user, 4])
                current_user = str(code).lstrip(" ")

                try:
                    get_user = conn.get_data("select RFID from user where RFID like %s", [current_user])
                    if get_user[0]:
                        print("Gebruiker ingescand")
                except IndexError:
                    print("Onbekende gebruiker ingescand")
                    current_user = "0"

                if current_user != "0":
                    get_latest_data = conn.get_data("select `Values` from datahistory "
                                                    "where User_RFID like %s "
                                                    "and `Values` like 'IN' or `Values` like 'OUT' "
                                                    "order by Date desc limit 1", [current_user])
                    try:
                        if get_latest_data[0].get("Values") == "IN":
                            print("User OUT")
                            conn.set_data('Insert into datahistory '
                                          'values (null, null, %s, (select rfid from user where RFID like %s), '
                                          '(select idSensoren from sensoren where idSensoren like %s))',
                                          ["OUT", current_user, 4])
                            current_user = "0"

                        elif get_latest_data[0].get("Values") == "OUT":
                            print("User IN")
                            conn.set_data('Insert into datahistory '
                                          'values (null, null, %s, (select rfid from user where RFID like %s), '
                                          '(select idSensoren from sensoren where idSensoren like %s))',
                                          ["IN", current_user, 4])

                    except IndexError:
                        print("New user IN")
                        conn.set_data('Insert into datahistory '
                                      'values (null, null, %s, '
                                      '(select rfid from user where RFID like %s), '
                                      '(select idSensoren from sensoren where idSensoren like %s))',
                                      ["IN", current_user, 4])


setup()

z = threading.Thread(target=get_rfid_tag)
z.start()

x = threading.Thread(target=get_value_ldr)
x.start()

v = threading.Thread(target=get_gps_values)
v.start()

# Custom endpoint
endpoint = '/api/smartbike'


@app.route(endpoint + "/graph-data-speed", methods=["GET"])
def get_data_graph():
    user = '0'
    for rfid, ip in logged_in_users.items():
        if ip == request.remote_addr:
            user = rfid
    data = conn.get_data('Select avg(`Values`) as "Values", Date from datahistory '
                         'where TypeSensor like %s '
                         'and User_RFID like %s '
                         'group by day(Date)',
                         ["3", user])

    return jsonify(data), 200


@app.route(endpoint + "/graph-data-time", methods=["GET"])
def get_data_graph_time():
    user = '0'
    for rfid, ip in logged_in_users.items():
        if ip == request.remote_addr:
            user = rfid
    data = conn.get_data('Select Date, `Values` from datahistory '
                         'where User_RFID like %s '
                         'and `Values` between %s and %s ', [user, 'IN', 'OUT'])
    return jsonify(data), 200


@app.route(endpoint + "/graph-data-gps", methods=["GET"])
def get_data_graph_gps():
    data = conn.get_data('Select `Values` from datahistory '
                         'where User_RFID like %s '
                         'and TypeSensor like %s '
                         'order by date desc '
                         'limit 2', ["0", '2'])
    return jsonify(data), 200


@app.route(endpoint + "/account-login", methods=["POST", "GET"])
def login_data():
    json_data = request.get_json()
    if request.method == "POST":
        data = conn.get_data('Select * from user where Email like %s and Password like %s',
                             [request.form["email"], request.form["password"]])
        print(data)
        try:
            if data[0] is not None:
                logged_in_users[data[0].get('RFID')] = request.remote_addr
                return redirect("http://192.168.0.177/data.html", code=200)
        except IndexError:
            return jsonify(message="Error: E-mailadres of wachtwoord verkeerd"), 204


@socketio.on("change_status_led")
def power_button():
    if GPIO.input(led_voor) == 0:
        GPIO.output(led_voor, GPIO.HIGH)
        socketio.emit("data", "led aan")
        conn.set_data("INSERT into datahistory "
                      "VALUES (null, null, %s, (select rfid from user where RFID like %s), %s)", ["ON", "0", "4"])
    else:
        GPIO.output(led_voor, GPIO.LOW)
        socketio.emit("data", "led uit")
        conn.set_data("INSERT into datahistory "
                      "VALUES (null, null, %s, (select rfid from user where RFID like %s), %s)", ["OFF", "0", "4"])


@socketio.on("connect")
def connecting():
    socketio.emit("connect")
    print("Connection with client established")


if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port="5000")
