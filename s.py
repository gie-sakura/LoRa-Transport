from network import LoRa
import binascii
import machine
import network
import socket
import sys
import time

import swlp

ANY_ADDR = b'FFFFFFFFFFFFFFFF'
file_tb_sent = "addio2000b.txt"

lora = LoRa(mode=LoRa.LORA)
# Create socket
try:
    the_sock = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
except socket.error:
    exit('Error creating socket.')

my_lora_address = binascii.hexlify(network.LoRa().mac())
dest_lora_address = ANY_ADDR

try:
    file = open(file_tb_sent,"rb")
    payload = file.read()
    file.close()
except:
    print("Unable to open file: ", file_tb_sent)

sent, retrans = swlp.tsend(payload, the_sock, my_lora_address, dest_lora_address)

# Done.
print("\nTRANSMISSION OVER")
print("Segments sent:\t\t" + str(sent) )
print("Segments retransmitted:\t" + str(retrans))

