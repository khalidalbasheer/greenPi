from flask import Flask, jsonify
import time
import threading
import socket
import re
import os
import sqlite3
import configparser
from datetime import datetime, timedelta
from firebase_admin import credentials, messaging, initialize_app

app = Flask(__name__)

@app.route('/', methods=['GET'])
def is_work():
    return 'The process work'

@app.route('/irr/<amount>', methods=['GET'])
def irrigationcommand(amount):
    try:
        global motor_node_ip
        global motor_node_port
        print(f'{datetime.now()}\tSending comand')
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((motor_node_ip, int(motor_node_port)))
        time.sleep(2)
        s.sendall(str.encode(amount+'\n'))
        s.close()
        if float(amount) > 0.0:
            INSERT_DATA = 'INSERT INTO IRRIGATION_TB (amount, i_date) VALUES (?, ?)'
            cur.execute(INSERT_DATA, (amount, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            con.commit()
        return 'OK'
    except Exception as e:
        return f'{datetime.now()}\tAn Error Occured: ({e})'

@app.route('/pushnotification/<title>/<body>', methods=['GET'])
def sendnotification(title=None, body=None):
    try:
        message = messaging.Message( 
        notification= messaging.Notification(title = title, body=body),
        token=registration_token
        )
        response = messaging.send(message)
        return jsonify({"Success": True}), 200
    except Exception as e:
        return f'An Error Occured: {e}'

def flaskThread():
    app.run(host='0.0.0.0', port=5000)

if __name__ == "__main__":
    notisent = False
    config = configparser.ConfigParser()
    DATA_PATH = 'data'
    if os.path.exists(DATA_PATH) == False:
        os.mkdir(DATA_PATH)
    con = sqlite3.connect(os.path.join(DATA_PATH,'database.db'), check_same_thread=False)
    cur = con.cursor()
    CREATE_TABLE = "CREATE TABLE IF NOT EXISTS IRRIGATION_TB (amount TEXT NOT NULL, i_date TEXT NOT NULL)"
    cur.execute(CREATE_TABLE)
    thread1 = threading.Thread(target= flaskThread, args=())
    thread1.start()

    cred = credentials.Certificate('serviceAccountKey.json')
    fire_app = initialize_app(cred)
    registration_token = 'dTU3AOCFQ6W1gdSWhSVjhN:APA91bFIPJeijAh2mYAPwS6yY9G4xx42FS2jo_iHGLedTJa-PJUHwpy50i8PaRaBIBikRYSqA0-yd2iZ8Hsbkmcsx3UU019PdRssDAFbEL0gJ2AjpB93IVR91yFe_JqKy7lNYv2zUVoX'
    time.sleep(1)

while True:
    config.read(os.path.join(DATA_PATH, 'configfile.ini'))
    irrigation = config['settings']
    motor_node_ip = irrigation['motor_node_ip']
    motor_node_port = irrigation['motor_node_port']
    master_node_ip = irrigation['master_node_ip']
    threshold_node = irrigation['threshold_node']
    irrigation_interval = int(irrigation['irrigation_interval'])
    irrigation_area = float(irrigation['irrigation_area'])
    irrigation_amount = float(irrigation['irrigation_amount'])
    auto_irrigation = True if irrigation['auto_irrigation'] == 'true' else False
    irrigation_threshold = int(irrigation['irrigation_threshold'])
    data_check_interval = float(irrigation['data_check_interval']) * 60
    total_amount = irrigation_area * irrigation_amount * 1000

    if threshold_node == 'average':
        mois_dt = cur.execute("SELECT * FROM MOISTURE_TB ORDER BY rowid desc LIMIT 10")
    else:
        mois_dt = cur.execute(f"SELECT * FROM MOISTURE_TB WHERE node_name='{threshold_node}' ORDER BY rowid desc LIMIT 10")
    moisture_level = [re.findall(r'\d+', d[1]) for d in mois_dt]
    flat_list = [x for xs in moisture_level for x in xs]
    flat_list = list(map(int,flat_list))
    moisture_average = sum(flat_list)/len(flat_list)

    start_date = datetime.today().date()
    end_date = start_date + timedelta(days=1)
    SELECT_DATA = f'''SELECT * FROM WEATHER_TB WHERE strftime('%Y-%m-%d',d_date) BETWEEN '{start_date}' and '{end_date}' '''
    w_dt = cur.execute(SELECT_DATA)

    w_datalist = list(w_dt.fetchall())
    if 'Rain' in [w[0] for w in w_datalist]:
        rainy_weather = True
    else:
        rainy_weather = False

    cur.execute('SELECT * FROM IRRIGATION_TB ORDER BY rowid DESC LIMIT 1')
    i_dt = cur.fetchall()
    if(len(i_dt) >0):
        last_irrigation_time = datetime.fromisoformat(i_dt[0][1])
    else:
        last_irrigation_time = datetime.now() - timedelta(days=100)
        print(last_irrigation_time)

    diff = datetime.now() - last_irrigation_time

    days, seconds = diff.days, diff.seconds
    last_irrigation_hours = days * 24 + seconds // 3600

    if auto_irrigation == True:
        if irrigation_interval < last_irrigation_hours:
            if not rainy_weather:
                if moisture_average < irrigation_threshold:
                    try:
                        irrigationcommand(str(total_amount))
                        print(f'{datetime.now()}\tIrrigation Started: Moisture Average = {moisture_average}')
                        notisent = False
                        sendnotification('Smart Irrigation System', 'Hello, the soil moisture level has dropped below the threshold level, so we will water the plants')
                    except Exception as e:
                        print(f'{datetime.now()}\tAn Error Occured: {e}')                
                elif moisture_average < (irrigation_threshold+10) and not notisent:
                    sendnotification('Smart Irrigation System', 'Hi, our plants have approached the threshold level of soil moisture, and we do not expect any rain, so we will water them soon')
                    notisent = True
                    print(f'{datetime.now()}\tMoisture Average: Notification is sent')
                else:
                    print(f'{datetime.now()}\tMoisture Average ({moisture_average}) above threshold')
            else:
                print(f'{datetime.now()}\tRainy Weather Tomorrow')
        else:
            print(f'{datetime.now()}\tIrrigation Interval')
    else:
        print(f'{datetime.now()}\tManual Irrigation')
    time.sleep(data_check_interval)
