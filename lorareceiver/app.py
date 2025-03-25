import sqlite3
from time import sleep
from datetime import datetime
from SX127x.LoRa import *
from SX127x.board_config import BOARD
import os
import json
from types import SimpleNamespace
import requests
import configparser

DATA_PATH = 'data'
if os.path.exists(DATA_PATH) == False:
    os.mkdir(DATA_PATH)
CREATE_TABLE = "CREATE TABLE IF NOT EXISTS MOISTURE_TB (node_name TEXT NOT NULL, moisture TEXT NOT NULL, rain TEXT NOT NULL, temprature TEXT NOT NULL, humidity TEXT NOT NULL, battery_level TEXT NOT NULL, d_date TEXT NOT NULL)"
con = sqlite3.connect(os.path.join(DATA_PATH,'database.db'), check_same_thread=False)
cur = con.cursor()
cur.execute(CREATE_TABLE)
con.commit()

config = configparser.ConfigParser()
config.read(os.path.join(DATA_PATH, 'configfile.ini'))
irrigation = config['settings']
rasp_ip = irrigation['master_node_ip']

# reg_exp = re.compile("[a-z]{1}:[0-9]+$")
# pattern = re.compile(r'\{\?:[^{}]}')
def restart_program():
    os.execv(sys.executable, ['python3'] + sys.argv)
BOARD.setup()
class LoRaRcvCont(LoRa):
    def __init__(self, verbose=False):
        super(LoRaRcvCont, self).__init__(verbose)
        self.set_mode(MODE.SLEEP)
        self.set_dio_mapping([0] * 6)
    def start(self):
        self.reset_ptr_rx()
        self.set_mode(MODE.RXCONT)
        while True:
            sleep(.5)
            rssi_value = self.get_rssi_value()
            status = self.get_modem_status()
            sys.stdout.flush()
    def on_rx_done(self):
        print("\nReceived: ")
        self.clear_irq_flags(RxDone=1)
        payload = self.read_payload(nocheck=True)
        timestamp = datetime.now().timestamp()
        moisture_data = bytes(payload).decode("utf-8",'ignore').replace("\u0000", "")
        try:
            jdata = json.loads(moisture_data, object_hook= lambda d: SimpleNamespace(**d))
            INSERT_DATA = 'INSERT INTO MOISTURE_TB (node_name, moisture, rain, temprature, humidity, battery_level, d_date) VALUES (?, ?, ?, ?, ?, ?, ?)'
            d_date = datetime.now()
            cur.execute(INSERT_DATA, (jdata.node_name, jdata.moisture, jdata.rain, jdata.temprature, jdata.humidity, jdata.battery_level, d_date.strftime('%Y-%m-%d %H:%M:%S')))
            con.commit()
            url = f'http://{rasp_ip}:4000/send'
            urldata = {'node_name':jdata.node_name, 'moisture':jdata.moisture, 'rain':jdata.rain, 'temprature':jdata.temprature, 'humidity':jdata.humidity, 'battery_level':jdata.battery_level, 'd_date':d_date.strftime('%Y-%m-%d %H:%M:%S')}
            headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
            requests.post(url, json=urldata, headers=headers)
            print(jdata.node_name, jdata.moisture, jdata.rain, jdata.temprature, jdata.humidity, jdata.battery_level)
            print(datetime.fromtimestamp(timestamp))
        except ValueError:
            print('Decoding JSON has failed')
            print(moisture_data)
        self.set_mode(MODE.SLEEP)
        self.reset_ptr_rx()
        self.set_mode(MODE.RXCONT)
        restart_program()

lora = LoRaRcvCont(verbose=False)
lora.set_mode(MODE.STDBY)
#  Medium Range  Defaults after init are 434.0MHz, Bw = 125 kHz, Cr = 4/5, Sf = 128chips/symbol, CRC on 13 dBm
lora.set_pa_config(pa_select=1)

try:
    lora.start()
except KeyboardInterrupt:
    sys.stdout.flush()
    print("")
    sys.stderr.write("KeyboardInterrupt\n")
finally:
    sys.stdout.flush()
    print("")
    lora.set_mode(MODE.SLEEP)
    BOARD.teardown()
