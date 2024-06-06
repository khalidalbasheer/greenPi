import sys
from time import sleep
from SX127x.LoRa import *
from SX127x.LoRaArgumentParser import LoRaArgumentParser
from SX127x.board_config import BOARD

BOARD.setup()

class LoRaBeacon(LoRa):
    def __init__(self, verbose=False, wait = 1, single = True, amount = 0.0):
        super(LoRaBeacon, self).__init__(verbose)
        self.set_mode(MODE.SLEEP)
        self.set_dio_mapping([1,0,0,0,0,0])
        self.wait = wait
        self.single = single
        self.amount = amount

    def on_rx_done(self):
        print("\nRxDone")
        print(self.get_irq_flags())
        print(map(hex, self.read_payload(nocheck=True)))
        self.set_mode(MODE.SLEEP)
        self.reset_ptr_rx()
        self.set_mode(MODE.RXCONT)

    def on_tx_done(self):
        self.set_mode(MODE.STDBY)
        self.clear_irq_flags(TxDone=1)
        sys.stdout.flush()
        print("Command are sent")
        if self.single:
            sys.exit(0)
        sleep(self.wait)
        self.write_payload(list(bytes(f'open{self.amount}', encoding='utf8')))
        self.set_mode(MODE.TX)

    def on_cad_done(self):
        print("\non_CadDone")
        print(self.get_irq_flags())

    def on_rx_timeout(self):
        print("\non_RxTimeout")
        print(self.get_irq_flags())

    def on_valid_header(self):
        print("\non_ValidHeader")
        print(self.get_irq_flags())

    def on_payload_crc_error(self):
        print("\non_PayloadCrcError")
        print(self.get_irq_flags())

    def on_fhss_change_channel(self):
        print("\non_FhssChangeChannel")
        print(self.get_irq_flags())

    def start(self):
        print('Sending LoRa Command...')
        self.write_payload(list(bytes(f'open{self.amount}', encoding='utf8')))
        self.set_mode(MODE.TX)
        print('Starting LoRa Receiver...')
        sleep(1)
        # while True:
            # sleep(1)

# lora = LoRaBeacon(verbose=False, amount=0.1)
# lora.set_pa_config(pa_select=1)


# print(lora)
# assert(lora.get_agc_auto_on() == 1)

# try:
#     lora.start()
# except KeyboardInterrupt:
#     sys.stdout.flush()
#     print("")
#     sys.stderr.write("KeyboardInterrupt\n")
# finally:
#     sys.stdout.flush()
#     print("")
#     lora.set_mode(MODE.SLEEP)
#     print(lora)
#     BOARD.teardown()
