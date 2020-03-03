import serial
import struct
from vc0706_reg import *

PORT = '/dev/USB0'
BAUD = 38400

class SendPacket:

    def __init__(self, serial_nbr, command, d_len, *data):

        self.headers = struct.pack('BBBB', RET_PROTO, serial_nbr, command, d_len)
        self.data    = data if data else None

class RecvPacket:

    def __init__(self, proto, serial_nbr, command, d_len, status, *data):

        self.headers = struct.pack('BBBBB', REC_PROTO, serial_nbr, command, d_len)
        self.data    = data if data else None
        

def send_packet(serial, packet):
    serial.write(packet.headers)
    if packet.data:
        serial.write(packet.data)

def decode_packet(serial, packet):
    packet = struct.unpack('BBBBB', packet)
    proto, ser_nbr, command, status, d_len = packet
    print('Proto\tSer_nbr\tCommand\tStatus\tLength')
    print('{:02X}\t{:02X}\t{:02X}\t{:02X}\t{:02X}\t'.
            format(proto, ser_nbr, command, status, d_len))
    if packet.data:
        print(packet.data)



if __name__ == '__main__':

    packet = SendPacket(0, GEN_VERSION, 1)

    stream = serial.Serial(PORT, BAUD)
    stream.write(packet)

    reply = stream.read()
    decode_packet(reply)

