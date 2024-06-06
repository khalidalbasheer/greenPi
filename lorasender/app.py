from flask import Flask
import lorasender

app = Flask(__name__)

@app.route('/', methods=['GET'])
def is_work():
    return 'The process work'

@app.route('/irrigate/<amount>', methods=['GET'])
def irrigationlora(amount):
    try:
        print('Start sending comand')
        lora = lorasender.LoRaBeacon(verbose=False, amount=amount)
        lora.set_pa_config(pa_select=1)
        assert(lora.get_agc_auto_on() == 1)
        lora.start()
        return 'OK'
    except Exception as e:
        return f'An Error Occured: ({e})'

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3000)