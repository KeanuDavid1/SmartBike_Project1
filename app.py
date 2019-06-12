import time
from datetime import datetime
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
if str(ips).split(' ')[0].lstrip("\\b\'") == "169.254.10.1":
    lcd.send_message(str(ips).split(' ')[1])
else:
    lcd.send_message(str(ips).split(' ')[0].lstrip("\\b\'"))

# python3.5 /home/keanu/tmp/pycharm_project_301/app.py

led_voor = 27
led_achter = 17

current_user = "0"
logged_in_users = {}
user_lights_input = False


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
        global user_lights_input

        if user_lights_input:
            user_lights_input = False
            time.sleep(30)

        if licht_waarde < 50:
            status = 1
        else:
            status = 0

        if status == 1 and GPIO.input(led_voor) == 0:
            GPIO.output(led_voor, GPIO.HIGH)
            GPIO.output(led_achter, GPIO.HIGH)
            socketio.emit("data", "Aan")
            conn.set_data("INSERT into datahistory "
                          "VALUES (null, null, %s, (select rfid from user where RFID like %s), %s)",
                          ["ON", current_user, "5"])
        elif status == 0 and GPIO.input(led_voor) == 1:
            GPIO.output(led_voor, GPIO.LOW)
            GPIO.output(led_achter, GPIO.LOW)
            socketio.emit("data", "Uit")
            conn.set_data("INSERT into datahistory "
                          "VALUES (null, null, %s, (select rfid from user where RFID like %s), %s)",
                          ["OFF", current_user, "5"])

        # print(acc.get_speed())

        time.sleep(5)

        # ip idres check

        if str(ips).split(' ')[0].lstrip("\\b\'") == "169.254.10.1":
            lcd.init_LCD()
            lcd.send_message(str(ips).split(' ')[1])
        else:
            lcd.init_LCD()
            lcd.send_message(str(ips).split(' ')[2].lstrip("\\b\'"))


def get_gps_values():
    with serial.Serial('/dev/ttyS0', 9600, timeout=1) as ser:
        while True:
            line = ser.readline()
            # print("Getting GPS values...")
            # print("Recieved GPS data: %s" % line)
            if str(line).find('GPGGA') != -1:
                msg = pynmea2.parse(str(line).lstrip('b\'').rstrip('\\r\\n\''))
                valueX = msg.latitude
                valueY = msg.longitude
                print(msg)
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
                        socketio.emit("RFID-tag", str(code).lstrip(" "))
                except IndexError:
                    print("Onbekende gebruiker ingescand")
                    socketio.emit("RFID-tag", str(code).lstrip(" "))
                    current_user = "0"

                if current_user != "0":
                    get_latest_data = conn.get_data("select `Values` from datahistory "
                                                    "where User_RFID like %s "
                                                    "and `Values` like 'IN' or `Values` like 'OUT' "
                                                    "order by Date desc limit 1", [current_user])
                    try:
                        if get_latest_data[0].get("Values") == "IN":
                            lcd.second_row()
                            lcd.send_message("User OUT")
                            time.sleep(1)
                            print("User OUT")
                            conn.set_data('Insert into datahistory '
                                          'values (null, null, %s, (select rfid from user where RFID like %s), '
                                          '(select idSensoren from sensoren where idSensoren like %s))',
                                          ["OUT", current_user, 4])
                            current_user = "0"

                        elif get_latest_data[0].get("Values") == "OUT":
                            print("User IN")
                            lcd.second_row()
                            lcd.send_message("User IN")
                            time.sleep(1)
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

# API -----------------------


# Custom endpoint
endpoint = '/api/smartbike'


@app.route(endpoint + "/user/graph-data-speed", methods=["GET"])
def get_data_graph():
    user = '0'
    for ip, rfid in logged_in_users.items():
        if ip == request.remote_addr:
            user = rfid
            print(user)
    data = conn.get_data('Select avg(`Values`) as "Values", Date from datahistory '
                         'where TypeSensor like %s '
                         'and User_RFID like %s '
                         'group by day(Date)',
                         ["3", user])
    return jsonify(data), 200


@app.route(endpoint + "/user/graph-data-time", methods=["GET"])
def get_data_graph_time():
    user = '0'
    for ip, rfid in logged_in_users.items():
        if ip == request.remote_addr:
            user = rfid
    data = conn.get_data('Select Date, `Values` from datahistory '
                         'where User_RFID like %s '
                         'and `Values` between %s and %s ', [user, 'IN', 'OUT'])
    print(data)
    total_time = 0
    dict_of_time = {}
    day = ""
    print(data[0].get('Date'))
    for i in range(0, len(data)):
        # print("Getting more time...")
        date = data[i].get('Date')
        value = data[i].get('Values')
        if value == 'IN':
            # print('Setting IN time!')
            global IN_time
            IN_time = date
        if value == 'OUT':
            # print('Setting OUT time!')
            global OUT_time
            OUT_time = date
            timediff = OUT_time - IN_time
            print(timediff.seconds)
            if day in dict_of_time:
                print("Adding time to day...")
                dict_of_time[data[i].get('Date').date().strftime("%d %b")] += timediff.seconds
            else:
                print("Adding day to dictionary...")
                dict_of_time[data[i].get('Date').date().strftime("%d %b")] = timediff.seconds
                print(dict_of_time)
            total_time += timediff.seconds
    sorted_dict = sorted(dict_of_time.items())
    return jsonify(sorted_dict), 200


@app.route(endpoint + "/user/graph-data-gps", methods=["GET"])
def get_data_graph_gps():
    data = conn.get_data('Select `Values` from datahistory '
                         'where User_RFID like %s '
                         'and TypeSensor like %s '
                         'order by date desc '
                         'limit 2', ["0", '2'])
    return jsonify(data), 200


@app.route(endpoint + "/user/extra-info-avgspeed", methods=["GET"])
def get_avg_speed():
    user = '0'
    for ip, rfid in logged_in_users.items():
        if ip == request.remote_addr:
            user = rfid
    data = conn.get_data('select avg(`Values`) as "avg" from datahistory '
                         'where TypeSensor like %s '
                         'and User_RFID like %s', ["3", user])
    return jsonify(data), 200


@app.route(endpoint + "/user/extra-info-maxspeed", methods=["GET"])
def get_max_speed():
    user = 0
    for ip, rfid in logged_in_users.items():
        if ip == request.remote_addr:
            user = rfid
    data = conn.get_data('select max(`Values`) as "max" from datahistory '
                         'where TypeSensor like %s '
                         'and User_RFID like %s', ["3", user])
    return jsonify(data), 200


@app.route(endpoint + '/user/logout', methods=['POST'])
def user_logout():
    logged_in_users.pop(request.remote_addr, None)
    return jsonify(message="User uitgelogd"), 200


# Account-login/aanmaken API ---------------------------------------


@app.route(endpoint + "/user/login", methods=["POST"])
def login_data():
    json_data = request.get_json()
    if request.method == "POST":
        data = conn.get_data('Select * from user where Email like %s and Password like %s',
                             [json_data["Email"], json_data["Password"]])
        try:
            if data[0] is not None:
                print("User gevonden in database.")
                if logged_in_users:
                    print("Ingelogde users gevonden")
                    for ip, rfid in logged_in_users.items():
                        print(rfid, ip)
                        if ip == request.remote_addr and rfid != data[0].get('RFID'):
                            print("Dubble entry")
                            return jsonify(message="Er is al een andere user ingelogd op jouw IP-adres"), 200
                        else:
                            logged_in_users[request.remote_addr] = data[0].get('RFID')
                            return jsonify(message='Changing user'), 200
                else:
                    print("Geen users ingelogd")
                    logged_in_users[request.remote_addr] = data[0].get('RFID')
                    return jsonify(message='Logging in'), 200
        except IndexError:
            return jsonify(message="E-mailadres of wachtwoord verkeerd"), 200


@app.route(endpoint + "/user/account-aanmaken", methods=["POST"])
def create_account():
    json_data = request.get_json()
    if request.method == "POST":
        data = conn.get_data('Select * from user where RFID like %s ',
                             [json_data["RFID"]])
        try:
            if data[0] is not None:
                print("User gevonden in database.")
                return jsonify(message="User bestaat al"), 200
        except IndexError:
            conn.set_data('Insert into user(rfid, name, firstname, email, Phone, password) '
                          'values (%s, %s, %s, %s, %s, %s)',
                          [json_data['RFID'], json_data['Fnaam'], json_data['Vnaam'], json_data['Email'],
                           ["0"], json_data['Password']])
            if logged_in_users:
                for ip, rfid in logged_in_users.items():
                    if ip == request.remote_addr and rfid != json_data['RFID']:
                        print("Dubble entry")
                        logged_in_users[request.remote_addr] = json_data['RFID']
                        print("Andere user op IP: '{}' uitgelogd".format(request.remote_addr))
                        return jsonify(message='Success!'), 200
                    else:
                        logged_in_users[request.remote_addr] = json_data['RFID']
                        return jsonify(message='Success!'), 200
            else:
                logged_in_users[request.remote_addr] = json_data['RFID']
                return jsonify(message='Success!'), 200


# Account page API -------------------------------------------------

@app.route(endpoint + "/user/update", methods=["PUT"])
def post_user_date_update():
    json_data = request.get_json()
    user = 0
    for ip, rfid in logged_in_users.items():
        if ip == request.remote_addr:
            user = rfid
    try:
        data = conn.get_data("Select * from user where Email like %s", json_data['Email'])
        if data[0] is not None:
            return jsonify(message="Dit e-mailadres is al in gebruikt"), 200
    except IndexError:
        if user != 0:
            if request.method == "PUT":
                conn.set_data('Update user set Name = %s, FirstName = %s, Email = %s, Password = %s '
                              'where RFID = %s',
                              [json_data['Fnaam'], json_data['Vnaam'], json_data['Email'], json_data['Password'],
                               user])
                return jsonify(message="Gegevens zijn aangepast"), 200
        else:
            return jsonify(message="Je bent niet ingelogt"), 200


@app.route(endpoint + "/user", methods=["GET"])
def get_user_data():
    user = ''
    for ip, rfid in logged_in_users.items():
        if ip == request.remote_addr:
            user = rfid
            print(user)
    print(logged_in_users)
    if request.method == "GET":
        data = conn.get_data("Select * from user where RFID like %s", [user])
        return jsonify(data), 200


@app.route(endpoint + "/user/check", methods=['GET'])
def check_if_logged_in():
    user = 0
    for ip, rfid in logged_in_users.items():
        if ip == request.remote_addr:
            user = rfid
    if user != 0:
        data = conn.get_data('select * from user where RFID like %s', [user])
        return jsonify(data), 200
    else:
        return jsonify(message="User niet ingelogd"), 200


# Socketio --------------------------------------------------

@socketio.on("change_status_led_on")
def power_light():
    user = 0
    for ip, rfid in logged_in_users.items():
        if ip == request.remote_addr:
            user = rfid
    if user != 0:
        GPIO.output(led_voor, GPIO.HIGH)
        GPIO.output(led_achter, GPIO.HIGH)
        socketio.emit("data", "Aan")
        global user_lights_input
        user_lights_input = True
        conn.set_data("INSERT into datahistory "
                      "VALUES (null, null, %s, (select rfid from user where RFID like %s), %s)", ["ON", "0", "4"])


@socketio.on("change_status_led_off")
def power_light_off():
    user = 0
    for ip, rfid in logged_in_users.items():
        if ip == request.remote_addr:
            user = rfid
    if user != 0:
        GPIO.output(led_voor, GPIO.LOW)
        GPIO.output(led_achter, GPIO.LOW)
        socketio.emit("data", "Uit  ")
        global user_lights_input
        user_lights_input = True
        conn.set_data("INSERT into datahistory "
                      "VALUES (null, null, %s, (select rfid from user where RFID like %s), %s)", ["OFF", "0", "4"])


@socketio.on("connect")
def connecting():
    socketio.emit("connect")
    print("Connection with client established")


if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port="5000")
