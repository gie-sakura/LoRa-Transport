import pycom
import time
import ufun

RED = 0xFF0000
YELLOW = 0xFFFF33
GREEN = 0x007F00
OFF = 0x000000
n=1

def set_led_to(color=GREEN):
    pycom.heartbeat(False) # Disable the heartbeat LED
    pycom.rgbled(color)
def flash_led_to(color=GREEN):
    set_led_to(color)
colores={}
while  True:
	color = input ("Que color? ")
	print(color)
	if (color.lower()=='rojo'):
		colores[n] = [color]
		n= n+1
		flash_led_to(RED)
		time.sleep(2)
	elif (color.lower() == 'amarillo'):
		colores[n] = [color]
		n= n+1
		flash_led_to(YELLOW)
		time.sleep(2)
	elif(color.lower()== 'verde'):
		colores[n] = [color]
		n= n+1
		flash_led_to(GREEN)
		time.sleep(2)
	elif(color.lower()== 'consulta'):
   		print (colores)
   	else: set_led_to(OFF)