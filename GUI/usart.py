from serial import Serial
import struct
import time

PORT = '/dev/ttyUSB0'
BAUD = 9600

com = Serial(PORT, BAUD)
com.flush()

com.close()



try:
    com.open()
    print('Sending!')
    com.write(struct.pack('B', 1))

    status = struct.unpack('B', com.read())[0]
    data = struct.unpack('B', com.read())[0]

    print('[AVR] Status: {}'.format(hex(status)))
    print('[AVR] Data:   {}'.format(hex(data)))
    

    
finally:
    com.close()

