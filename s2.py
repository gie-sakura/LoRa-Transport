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
file_tb_sent = "addio2000b.txt"
Dispositivos={0:0}

lora = LoRa(mode=LoRa.LORA)
# Create socket
try:
    the_sock = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
except socket.error:
    exit('Error creating socket.')
# get LoRa MAC address
my_lora_address = binascii.hexlify(network.LoRa().mac())
dest_lora_address = ANY_ADDR
try:
    file = open(file_tb_sent,"rb")
    payload = file.read()
    file.close()
except:
    print("Unable to open file: ", file_tb_sent)
while True:
	opcion = input("Usted Desea: ")
	if(opcion.lower()=="manual"):
		Dispositivos=Descubrimiento.descubrir(the_sock, my_lora_address, dest_lora_address)
		print(type(Dispositivos))
		print(Dispositivos)
		while True:
			dir1= input("indique a quien enviar: ")
			if Dispositivos.has_key(dir1):
				dest_lora_address=Dispositivos.get(dir1)
				sent, retrans = swlpv2.tsend(payload, the_sock, my_lora_address, dest_lora_address)
			elif dir1=="salir":
				break
			else:
				print("No está en la lista")
	if(opcion.lower()=="automatico"):
		sent, retrans = swlpv2.tsend(payload, the_sock, my_lora_address, dest_lora_address)
		# Done.
		print("\nTRANSMISSION OVER")
		print("Segments sent:\t\t" + str(sent) )
		print("Segments retransmitted:\t" + str(retrans))