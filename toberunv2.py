from network import LoRa
import socket
import machine
import time
import binascii
import network
import ufun
import pycom

# Name of your team
team_name = 'TeamB'

RED = 0xFF0000
YELLOW = 0xFFFF33
GREEN = 0x007F00
OFF = 0x000000

def set_led_to(color=GREEN):
    pycom.heartbeat(False) # Disable the heartbeat LED
    pycom.rgbled(color)

def flash_led_to(color=GREEN, t1=1):
    set_led_to(color)
    time.sleep(t1)
    set_led_to(OFF)

# initialize LoRa in LORA mode
# more params can also be given, like frequency, tx power and spreading factor
lora = LoRa(mode=LoRa.LORA)

# get LoRa MAC address
loramac = binascii.hexlify(network.LoRa().mac())
print(loramac)
loramac2 = binascii.unhexlify(loramac)
# create a raw LoRa socket
s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)

while True:
    # get any data received...
    s.setblocking(False)
    data = s.recv(64)
    data2=str(data)
    if data != b'':
        macorigen, sender, receiver, message=data2.split(",")
        print(data)
        largo = len(message)
        messagef = message[:largo-1]
        print(messagef)
        LoraStats = lora.stats()            # get lora stats (data is tuple)
        print(LoraStats)
        if messagef.lower() =="rojo":
            flash_led_to(RED)
            time.sleep(5)

    # wait a random amount of time
    rat = machine.rng() & 0x05
    time.sleep(rat)
