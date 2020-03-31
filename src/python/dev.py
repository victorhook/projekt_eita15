import socket

try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('192.168.0.7', 13334))
    sock.listen(0)

    con = sock.accept()[0].makefile('rb')

    


finally:

    try:
        sock.close()
        con.close()

    except:
        pass