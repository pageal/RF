# used with Smakn 433Mhz Rx Tx modules
import os
import time
import thread
import threading
import pigpio
import virtual_wire as wv

#import wiringPI as wiring_pi
#pin_TX = 17
#pin_RX = 18
#os.system("gpio export {} in".format(pin_RX))
#os.system("gpio -g mode {} in".format(pin_RX))          
#os.system("gpio export {} out".format(pin_TX))
#os.system("gpio -g mode {} out".format(pin_TX))          

class receiver():
    def __init__(self, bcm_pin_rx, bits_per_sec=20, gpio_obj = None):
        self._bcm_pin_rx = bcm_pin_rx
        self._bits_per_sec = bits_per_sec
        self._gpio_stop = False
        if(gpio_obj != None):
            self._gpio_stop = True
        self._gpio_obj = gpio_obj
        self._rx_pin = wv.rx(self._gpio_obj, self._bcm_pin_rx, self._bits_per_sec)
        self._thread = threading.Thread(target=self._the_thread)
        self._stop = False

    def read_msg(self, bcm_pin_rx, bits_per_sec=20, gpio_obj = None):
        if not process_exists("pigpiod"):
            try:
                os.system("sudo pigpiod")
                time.sleep(5)
            except Exception as e:
                print(str(e))

        if(gpio_obj == None):    
            gpio_obj = pigpio.pi() 

        rx_cleanup = False
        if(self._rx_pin == None):
            self._rx_pin = wv.rx(gpio_obj, bcm_pin_rx, bits_per_sec)
            rx_cleanup = True

        msg = ""
        try:
            while self._rx_pin.ready():
                msg = "".join(chr (c) for c in self._rx_pin.get())
                time.sleep(0.05)
            
        except Exception as e:
            print("read failed with exception" + str(e))

        if(len(msg)):
            print("received: " + msg)
        if(rx_cleanup):
            self._rx_pin.cancel()
        return msg

    def _the_thread(self):
        print("rcv thread started")
        while(self._stop != True):
            self.read_msg(self._bcm_pin_rx, self._bits_per_sec, self._gpio_obj)
            time.sleep(1000)


    def start(self):
        self._stop = False
        self._thread.start()

    def stop(self):
        self._stop = True
        self._rx_pin.cancel()
        if(self._gpio_stop == True):
            self._gpio_obj.stop()
        
        


def process_exists(processname):
    tmp = os.popen("ps -Af").read()
    proccount = tmp.count(processname)

    if proccount > 0:
        return True
    return False
    
def send_msg(bcm_pin_tx, msg, bits_per_sec=20, gpio_obj = None):
    if not process_exists("pigpiod"):
        try:
            os.system("sudo pigpiod")
            time.sleep(5)
        except Exception as e:
            print(str(e))
    stop_gpio = False
    if(gpio_obj == None):    
        gpio_obj = pigpio.pi()
        stop_gpio = True

    tx_pin = wv.tx(gpio_obj, bcm_pin_tx, bits_per_sec)

    while not tx_pin.ready():
        time.sleep(0.1)

    try:
        tx_pin.put(msg)
        print("sent: " + msg)
    except Exception as e:
        print("send failed with exception" + str(e))

    tx_pin.cancel()
    if(stop_gpio):
        gpio_obj.stop()


if __name__ == "__main__":

    if not process_exists("pigpiod"):
        try:
            os.system("sudo pigpiod")
            time.sleep(5)
        except Exception as e:
            print(str(e))

    gpio_obj = pigpio.pi()
    rcv = receiver(18, 2000, gpio_obj)
    rcv.start()
    time.sleep(1)
    send_msg(17, "1234567890", 2000, gpio_obj)
