import io
import picamera 
import select
import socket
import struct
import sys
import time
import threading


HOST           = '192.168.0.7'
PORT           = 13337
RESOLUTION     = (1280, 720)
FRAMERATE      = 30


class VideoBuffer:

    """ 
        The VideoBuffer is used by the PiCamera API, to write
        data that is sampled from the camera.
        By overwriting the write() method, we can take control
        of what happens between samples, so that we can send the
        data through a network socket.
    """

    def __init__(self, tcp_socket):
        self.connection = tcp_socket.makefile('wb')
        self.stream = io.BytesIO()
    
    """
        With PiCamera's recording() function, with MJPEG format,
        it seperates the image frames with the combinations of
        FF D8, as specified by the MJPEG specification.
        This makes it easy to seperate new frames from old ones,
        and when a new one is detected, we send the old one
    """
    def write(self, data):

        # FF D8 = New JPEG frame, time to send the one in buffer!
        if data.startswith(b'\xff\xd8'):

            # Get lenth of current frame
            img_size = self.stream.tell()

            # Ensure it's not 0
            if img_size:

                # Write image length and flush before we send data
                 # <L> = Unsigned long, little endian
                self.connection.write(struct.pack('<L', img_size))
                self.connection.flush()

                # Rewind stream to start and write to the connection
                self.stream.seek(0)
                self.connection.write(self.stream.read(img_size))

                # Rewind and truncate stream
                self.stream.seek(0)

        # Append new data to the stream
        self.stream.write(data)

if __name__ == '__main__':

    try:

        # Create a socket and open a connection 
        tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_socket.connect((HOST, PORT))

        # Buffer to store image frames, used by the PiCamera API
        video_buffer = VideoBuffer(tcp_socket)

        with picamera.PiCamera(resolution = RESOLUTION, framerate = FRAMERATE) as camera:

            # Time to start recording!
            camera.start_recording(video_buffer, format('mjpeg'))
            camera_running = True

            # Enter infinite-loop until host wants to quit
            while camera_running:
                
                # Constantly check if there's any data in the socket
                # If there is, the host wants to quit!
                input_data = select.select([tcp_socket], [], [], 0)[0]
                if input_data:
                    camera_running = False

            print('Done!')
            # Host is done, time to cleanup!

    finally:
        try:
            # Close the streams properly
            tcp_socket.shutdown(socket.SHUT_RDWR)
            tcp_socket.close()

        except Exception as e:
            # Failed to close streams? Not much to do
            print('Exception: %s' % e)
            pass