from network import LoRa
import socket
import machine
import time
import binascii
import uhashlib
import network
import ubinascii
import struct
import sys

# Name of your team
MAX_PKT_SIZE = 128
HEADER_FORMAT = "!8s8sHHB3s"
HEADER_SIZE = 24
DATA_PACKET = False
ANY_ADDR = b'FFFFFFFF'

# header structure:
# 8B: source addr (last 8 bytes)
# 8B: dest addr (last 8 bytes)
# 2B: seqnum 
# 2B: acknum
# 1B: flags
# 3B: checksum

"""# initialize LoRa in LORA mode
# more params can also be given, like frequency, tx power and spreading factor
lora = LoRa(mode=LoRa.LORA)

# get LoRa MAC address
loramac = binascii.hexlify(network.LoRa().mac())
print(loramac)

# create a raw LoRa socket
s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)"""
def make_packet(source_addr, dest_addr, seqnum, acknum, is_a_ack, last_pkt, content):
    
    flags = 0
    if last_pkt: flags = flags | (1<<0)
    if is_a_ack: flags = flags | (1<<4)

    check = get_checksum(content)

    header = struct.pack(HEADER_FORMAT, source_addr, dest_addr, seqnum, acknum, flags, check)

    return header + content

def unpack(packet):
    header  = packet[:HEADER_SIZE]
    content = packet[HEADER_SIZE:]
    sp, dp, seqnum, acknum, flags, check = struct.unpack(HEADER_FORMAT, header)
    is_a_ack = (flags >> 4) == 1
    last_pkt = (flags & 1)  == 1

    return sp, dp, seqnum, acknum, is_a_ack, last_pkt, check, content

def get_checksum(data):

    h = uhashlib.sha256(data)
    ha = ubinascii.hexlify(h.digest())
    return ha[-3:]

def descubrir(the_sock, SND_ADDR, RCV_ADDR):
    seqnum = 0
    acknum = 0
    sent    = 0
    retrans = 0
    cuenta=0
    last_pkt = True
    dispositivos={}
    text=SND_ADDR
    packet = make_packet(SND_ADDR, ANY_ADDR, seqnum, acknum, DATA_PACKET, last_pkt, text)
    send_time = time.time()
    sent += 1
    the_sock.settimeout(1)
    while True:
        try:
            print("buscando")
            the_sock.send(packet)
            data = the_sock.recv(MAX_PKT_SIZE)
            source_addr, dest_addr, seqnum, acknum, ack, final, content = unpack(data)
            ips = dispositivos.values()
            if(data != b'')and(content not in ips):
                print(data)
                dispositivos[seqnum] = [content]
                n+=1
                # wait a random amount of time
                rat = machine.rng() & 0x05
                time.sleep(rat)
        except socket.timeout:
            the_sock.send(packet)
            cuenta+=1
            print(cuenta)
        if(cuenta==10):
            break
    return dispositivos

def responder(the_sock,MY_ADDR, SND_ADDR):
    seqnum = 0
    acknum = 0
    sent    = 0
    retrans = 0
    last_pkt = True
    the_sock.setblocking(True)
    data = the_sock.recv(50)
    source_addr, dest_addr, seqnum, acknum, ack, last_pkt, check, content = unpack(packet)
    SND_ADDR = source_addr
    text=MY_ADDR
    packet = make_packet(MY_ADDR, SND_ADDR, seqnum, acknum, DATA_PACKET, last_pkt, text)
    send_time = time.time()
    sent += 1
    the_sock.setblocking(False)
    the_sock.send(packet)
    return source_addr
