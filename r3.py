from network import LoRa
import binascii
import machine
import network
import socket
import sys
import time

import swlpv2
import Descubrimiento

ANY_ADDR = b'FFFFFFFFFFFFFFFF'
# PM_lora_device = b'70b3d549964a4de5'

lora = LoRa(mode=LoRa.LORA)
try:
    the_sock = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
except socket.error:
    exit('Error creating socket.')

my_lora_address = binascii.hexlify(network.LoRa().mac())
print(my_lora_address)
sender_lora_address = ANY_ADDR

print("listo para recibir")
#ipor=Descubrimiento.responder(the_sock,my_lora_address,sender_lora_address)
#print(ipor)
while True:
	rcvd = swlpv2.trecv(the_sock, my_lora_address, sender_lora_address)
	print(rcvd)
	#if(rcvd!=sender_lora_address)
	#	sender_lora_address=rcvd
	print(sender_lora_address)
	print("The End.")
