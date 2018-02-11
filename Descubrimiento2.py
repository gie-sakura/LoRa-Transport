from network import LoRa
import socket
import machine
import time
import binascii
import network

# Name of your team
team_name = 'TeamB'

# initialize LoRa in LORA mode
# more params can also be given, like frequency, tx power and spreading factor
lora = LoRa(mode=LoRa.LORA)

# get LoRa MAC address
loramac = binascii.hexlify(network.LoRa().mac())
print(loramac)

# create a raw LoRa socket
s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)

def timeout(signum, frame):
    raise socket.timeout

while True:
    s.settimeout(5)
    # get any data received...
    try:
        s.setblocking(True)
        data = s.recv(64)
        if data != b'':
            print(data)
            LoraStats = lora.stats()           # get lora stats (data is tuple)
            print(LoraStats)
            s.setblocking(True)
            tbs = loramac
            print('Sending...'+str(tbs))
            s.send(tbs)
    except timeout:
        print("tiempo")
        break
    # wait a random amount of time
    #rat = machine.rng() & 0x05
    #time.sleep(rat)
