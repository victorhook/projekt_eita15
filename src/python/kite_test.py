import socket
sock = socket.socket()
sock.bind(())
sock.listen(0)
d = sock.accept()[0]
