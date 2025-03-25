from flask import Flask
import sys
from time import sleep
from SX127x.LoRa import *
from SX127x.board_config import BOARD
import RPi.GPIO as GPIO

BOARD.setup()
app = Flask(__name__)

@app.route('/', methods=['GET'])
def is_work():
    return 'The process works'

@app.route('/irrigate/<amount>', methods=['GET'])
def irrigationlora(amount):
    try:
        print('Sending LoRa Command...')
        lora.set_dio_mapping([1,0,0,0,0,0])
        lora.write_payload(list(bytes(f'open{amount}', encoding='utf8')))
        lora.set_mode(MODE.TX)
        sleep(1)
        print('LoRa command are sent...')
        return 'OK'
    except Exception as e:
        return f'An Error Occured: ({e})'

if __name__ == "__main__":
    GPIO.setmode(GPIO.BCM)
    lora = LoRa(verbose=False)
    lora.set_pa_config(pa_select=1)
    # assert(lora.get_agc_auto_on() == 1)
    app.run(host='0.0.0.0', port=3000)
