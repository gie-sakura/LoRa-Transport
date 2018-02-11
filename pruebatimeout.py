#import socket
import struct
import sys
import time
from socket import *
import signal

n = 0
try:
    the_sock = socket(AF_INET, SOCK_STREAM)
except:
    exit('Error creating socket.')
the_sock.settimeout(2)
#socket.setdefaulttimeout(2)
while True:
	try:
		#the_sock.settimeout(2)
		the_sock.setblocking(False)
		data = the_sock.recv(64)
		n+=1
		print("Hola"+str(n))
		#time.sleep(1)
	except timeout:
		print("tiempo")
		break
"""import socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(1)
try:
    s.send("Hola")
    print s.recv(1024)
except socket.timeout as e:
    print "Tiempo"""