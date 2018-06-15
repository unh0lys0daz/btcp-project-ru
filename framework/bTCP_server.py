#!/usr/local/bin/python3
import socket, argparse
from struct import *

#Handle arguments
parser = argparse.ArgumentParser()
parser.add_argument("-w", "--window", help="Define bTCP window size", type=int, default=100)
parser.add_argument("-t", "--timeout", help="Define bTCP timeout in milliseconds", type=int, default=100)
parser.add_argument("-o","--output", help="Where to store file", default="tmp.file")
args = parser.parse_args()

server_ip = "127.0.0.1"
server_port = 9001

#Define a header format
header_format = "!IHHBBHI"

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
sock.bind((server_ip, server_port))

def make_header(str_id, syn_nr, ack_nr, flags, win, data_len):
    checks = checksum(str_id, syn_nr, ack_nr, flags, win, data_len)
    bTCP_header = pack(header_format, str_id, syn_nr, ack_nr, flags, win, data_len, checks)
    return bTCP_header

expected = 0
syn = 0

filename = args.output
fh = open(filename, 'w')

data, addr = sock.recvfrom(1016)
(str_id_recv, syn_nr_r, ack_nr_r, flags_r, win_r, data_len_r, checks_r) = unpack("!IHHBBHI1000x")
header_sa = make_header(str_id_recv, 0, 0, SYN | ACK, 1000, 0, checks)
sock.sendto(header_sa + ("\x00" * 1000).encode('utf8'), addr)


while True:
    try:
        data, addr = sock.recvfrom(1016)
    except:
        continue
    (str_id_recv, syn_nr_r, ack_nr_r, flags_r, win_r, data_len_r, check    s_r, buf) = unpack("!IHHBBHI1000B",data)
    if flags_r == FIN:
        handle_fin(sock)
        fh.close()
        break
    if syn_nr_r == expected:
        expected +=1000
        syn += 1
        header = make_header(str_id_recv, syn, expected, ACK, 1000, 0, checks)

        sock.sendto(header + ("\x00" * 1000).encode('utf8'), addr)
        fh.write(buf[:data_len_r]
    else:
        continue

