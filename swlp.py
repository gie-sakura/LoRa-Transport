#!/usr/bin/env python
"""
Stop & Wait like protocol to be used on a LoRa raw channel

Based on https://github.com/arturenault/reliable-transport-protocol by Artur Upton Renault

Modified by: Pietro GRC dic2017
"""

import machine
import socket
import struct
import sys
import time
import uhashlib
import ubinascii

DEBUG_MODE = True

#
# BEGIN: Utility functions
#

MAX_PKT_SIZE = 128  # Must determine which is the maximum pkt size in LoRa...
HEADER_FORMAT = "!8s8sHHB3s"
HEADER_SIZE = 24
# header structure:
# 8B: source addr (last 8 bytes)
# 8B: dest addr (last 8 bytes)
# 2B: seqnum 
# 2B: acknum
# 1B: flags
# 3B: checksum 
PAYLOAD_SIZE = MAX_PKT_SIZE - HEADER_SIZE

DATA_PACKET = False
ANY_ADDR = b'FFFFFFFF'      # last 8 bytes

# Create a packet from the necessary parameters
def make_packet(source_addr, dest_addr, seqnum, acknum, is_a_ack, last_pkt, content):
    
    flags = 0
    if last_pkt: flags = flags | (1<<0)
    if is_a_ack: flags = flags | (1<<4)

    check = get_checksum(content)

    header = struct.pack(HEADER_FORMAT, source_addr, dest_addr, seqnum, acknum, flags, check)

    return header + content

# Break a packet into its component parts
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

def debug_printpacket(msg, packet, cont=False):
    sp, dp, seqnum, acknum, is_a_ack, last_pkt, check, content = unpack(packet)
    if cont:
        print("{}: s_p: {}, d_p: {}, seqn: {}, ackn: {}, ack: {}, fin: {}, check: {}, cont: {}".format(msg, sp, dp, seqnum, acknum, is_a_ack, last_pkt, check, content))
    else:
        print("{}: s_p: {}, d_p: {}, seqn: {}, ackn: {}, ack: {}, fin: {}, check: {}".format(msg, sp, dp, seqnum, acknum, is_a_ack, last_pkt, check))

def timeout(signum, frame):
    raise socket.timeout

#
# END: Utility functions
#

def tsend(payload, the_sock, SND_ADDR, RCV_ADDR):

    # Shortening addresses to save space in packet
    SND_ADDR = SND_ADDR[8:]
    RCV_ADDR = RCV_ADDR[8:]

    # identify session with a number between 0 and 255: NOT USED YET
    sessnum = machine.rng() & 0xFF  

    # Initialize counters et al
    seqnum = 0
    acknum = 0
    sent    = 0
    retrans = 0
    timeout_time    =  1    # 1 second
    estimated_rtt   = -1
    dev_rtt         =  1

    # Reads first block from string "payload"
    text    = payload[0:PAYLOAD_SIZE]    # Copying PAYLOAD_SIZE bytes header from the input string
    payload = payload[PAYLOAD_SIZE:]    # Shifting the input string
    # Checking if this is the last packet
    if (len(text) == PAYLOAD_SIZE) and (len(payload) > 0): 
        last_pkt = False
    else: 
        last_pkt = True 

    the_sock.setblocking(True)
    packet = make_packet(SND_ADDR, ANY_ADDR, seqnum, acknum, DATA_PACKET, last_pkt, text)
    the_sock.send(packet)
    send_time = time.time()
    sent += 1
    if DEBUG_MODE: debug_printpacket("sending 1st", packet)

    the_sock.settimeout(5)      # 5 seconds initial timeout.... LoRa is slow
    if not last_pkt:
        while True:
            try:

                # waiting for a ack
                the_sock.setblocking(True)
                ack = the_sock.recv(HEADER_SIZE)
                recv_time = time.time()

                # Unpack packet information
                ack_source_addr, ack_dest_addr, ack_seqnum, ack_acknum, ack_is_ack, ack_final, ack_check, ack_content = unpack(ack)
                if DEBUG_MODE: debug_printpacket("received ack", ack)

                if ack_final: break 

                # If valid, here we go!
                if ack_is_ack and (ack_acknum == acknum):

                    # RTT calculations
                    sample_rtt = recv_time - send_time
                    if estimated_rtt == -1:
                        estimated_rtt = sample_rtt
                    else:
                        estimated_rtt = estimated_rtt * 0.875 + sample_rtt * 0.125
                    dev_rtt = 0.75 * dev_rtt + 0.25 * abs(sample_rtt - estimated_rtt)
                    the_sock.settimeout(estimated_rtt + 4 * dev_rtt)
                    if DEBUG_MODE: print("setting timeout to", estimated_rtt + 4 * dev_rtt)

                    text    = payload[0:PAYLOAD_SIZE]   # Copying PAYLOAD_SIZE bytes header from the input string
                    payload = payload[PAYLOAD_SIZE:]    # Shifting the input string
                    # Checking if this is the last packet
                    if (len(text) == PAYLOAD_SIZE) and (len(payload) > 0): 
                        last_pkt = False
                    else: 
                        last_pkt = True 

                    # Increment sequence and ack numbers
                    seqnum += 1
                    acknum += 1

                    the_sock.setblocking(False)
                    packet = make_packet(SND_ADDR, ANY_ADDR, seqnum, acknum, DATA_PACKET, last_pkt, text)
                    the_sock.send(packet)
                    send_time = time.time()
                    sent += 1 
                    if DEBUG_MODE: debug_printpacket("sending new packet", packet, True)

                else:
                    if DEBUG_MODE: print("ERROR: packet received not valid")
                    raise socket.timeout

            except socket.timeout:
                if DEBUG_MODE: print("EXCEPTION!! Socket timeout: ", time.time())
                packet = make_packet(SND_ADDR, ANY_ADDR, seqnum, acknum, DATA_PACKET, last_pkt, text)
                the_sock.send(packet)
                if DEBUG_MODE: debug_printpacket("re-sending packet: ", packet)

                sent += 1
                retrans += 1

    print("RETURNING tsend")        
    return(sent,retrans)

#
#
#
def trecv(the_sock, MY_ADDR, SND_ADDR):

    # Shortening addresses to save space in packet
    MY_ADDR = MY_ADDR[8:]
    SND_ADDR = SND_ADDR[8:]

    # Buffer storing the received data to be returned
    rcvd_data = b""

    next_acknum = 0

    while True:
        # Receive first packet
        the_sock.setblocking(True)
        packet = the_sock.recv(MAX_PKT_SIZE)
        source_addr, dest_addr, seqnum, acknum, ack, last_pkt, check, content = unpack(packet) 
        if (dest_addr==MY_ADDR) or (dest_addr==ANY_ADDR):
            break
        else: 
            if DEBUG_MODE: debug_printpacket("DISCARDED received packet; not for me!!", packet)

    if DEBUG_MODE: debug_printpacket("received 1st packet", packet, True)

    checksum_OK = (check == get_checksum(content))
    if (checksum_OK) and (next_acknum == acknum):
        packet_valid = True
        rcvd_data += content
        next_acknum += 1
    else: 
        packet_valid = False

    # Sending first ACK
    ack_segment = make_packet(MY_ADDR, source_addr, seqnum, acknum, packet_valid, last_pkt, "")
    the_sock.setblocking(False)
    the_sock.send(ack_segment)
    if DEBUG_MODE: debug_printpacket("sent 1st ACK", ack_segment)

    the_sock.settimeout(5)      # 5 seconds timeout.... LoRa is slow
    if not last_pkt:
        while True:

            while True:
                # Receive every other packet
                the_sock.setblocking(True)
                packet = the_sock.recv(MAX_PKT_SIZE)
                source_addr, dest_addr, seqnum, acknum, ack, last_pkt, check, content = unpack(packet)
                if (dest_addr==MY_ADDR) or (dest_addr==ANY_ADDR):
                    if DEBUG_MODE: debug_printpacket("received packet", packet, True)
                    break
                else: 
                    if DEBUG_MODE: debug_printpacket("DISCARDED received packet; not for me!!", packet)

            checksum_OK = (check == get_checksum(content))

            # ACK the packet if it's correct; otherwise send NAK.
            if (checksum_OK) and (next_acknum == acknum):
                packet_valid = True
                rcvd_data += content
                next_acknum += 1
            else: 
                packet_valid = False

            ack_segment = make_packet(MY_ADDR, source_addr, seqnum, acknum, packet_valid, last_pkt, "")
            the_sock.setblocking(True)
            the_sock.send(ack_segment)
            if DEBUG_MODE: debug_printpacket("sending ACK", ack_segment)

            if last_pkt:
                break

    return rcvd_data

