import numpy as np
import socket
import pickle
import sys

from facerenderer import FaceRenderer
from tempfile import TemporaryFile



def recv_verts(conn: socket.socket):
    dump = b""
    while True:
        packet = conn.recv(1024)
        if not packet:
            return False, None

        dump += packet
        if dump[-6:] == b"ENDMSG":
            break
    
    dump2 = dump[:-5]

    if len(dump2) > 0:
        data = pickle.loads(dump2)
        return True, data
    return False, None



def entry():

    HOST = b"0.0.0.0"
    PORT = int(sys.argv[1])

    NUM_USERS = 2

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((HOST, PORT))
    sock.listen()

    clients: list[socket.socket] = []
    connected: list[bool] = []

    while (len(clients) < NUM_USERS):
        conn, addr = sock.accept()
        clients.append(conn)
        connected.append(True)
        print(f"Connected over {addr}")


    current = -1
    num_connected = 200
    while num_connected > 0:
        current = (current+1) % NUM_USERS
        if not connected[current]:
            continue

        print("Requesting vertices from client %d" % (current), end="... ")
        clients[current].sendall(b"VERTS")
        res, verts = recv_verts(clients[current])

        if res:
            print("received")
            print(verts[0])
            print(verts[1])
            print(verts[2])
        else:
            print("error receiving")
            connected[current] = False
            continue

        # clients[current].sendall(b"END")


    sock.shutdown(socket.SHUT_RDWR)
    sock.close()


entry()
