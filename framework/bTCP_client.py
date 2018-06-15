#!/usr/local/bin/python3
import socket, argparse, random
from struct import *
import time

SYN = 0x1
ACK = 0x2
FIN = 0x4
RST = 0x8

#Handle arguments
parser = argparse.ArgumentParser()
parser.add_argument("-w", "--window", help="Define bTCP window size", type=int, default=100)
parser.add_argument("-t", "--timeout", help="Define bTCP timeout in milliseconds", type=int, default=100)
parser.add_argument("-i","--input", help="File to send", default="tmp.file")
args = parser.parse_args()

destination_ip = "127.0.0.1"
destination_port = 9001

#bTCP header
header_format = "!IHHBBHI"
bTCP_header = pack(header_format, randint(0,100), syn_nr, ack_nr, flags, win, data_len, checks)
bTCP_payload = ""
udp_payload = bTCP_header

#UDP socket which will transport your bTCP packets
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(1000)
#send payload
sock.sendto(udp_payload, (destination_ip, destination_port))

def make_header(str_id, syn_nr, ack_nr, flags, win, data_len):
    header_format = "IHHBBHI"
    checks = checksum(str_id, syn_nr, ack_nr, flags, win, data_len)
    bTCP_header = pack(header_format, str_id, syn_nr, ack_nr, flags, win, data_len, checks)
    return bTCP_header

def connect_btcp(sock):
    payload = ("\x00" * 1000).encode('utf8')
    str_id = randint(1,1000)
    header_syn = make_header(str_id, 0, 0, SYN, 1000, 0)
    header_ack = make_header(str_id, 0, 0, ACK, 1000, 0)
    sock.sendto(header_syn + payload, (destination_ip, destination_port))
    try:
        data = sock.recv(1016)
    except:
        return 0
    (str_id_recv, syn_nr_r, ack_nr_r, flags_r, win_r, data_len_r, checks_r) = unpack("IHHBBHI1000x",data)
    if str_id_recv != str_id:
        return 0
    if (flags_r & RST) != 0:
        return 0
    if (flags_r & (SYN | ACK)) != (SYN | ACK):
        return 0
    return str_id

def make_payload(buf):
    size = 1000 - len(buf)
    payload = buf + ("\x00" * size).encode('utf8')
    return payload

def send_file(sock, filename, str_id):
    fh = open(filename)
    syn_nr = 0
    ack_nr = 0
    while fh:
        buf = fh.read(1000)
        payload = make_payload(buf)
        header = make_header(str_id, syn_nr, ack_nr, ACK, 1000, len(buf))
        sock.sendto(header + payload, (destination_ip, destination_port))
        try:
            data = sock.recv(1008)
        except:
            data = None
        if not data:
            continue
        (str_id_recv, syn_nr_r, ack_nr_r, flags_r, win_r, data_len_r, checks_r) = unpack("IHHBBHI1000x",data)
        if ack_nr_r == (syn_nr + 1000):
            syn_nr += 1000
            ack_nr += 1
        else:
            fh.seek(-len(buf), 1)

