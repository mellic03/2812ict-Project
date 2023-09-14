import numpy as np
import socket
import pickle
import sys

from facerenderer import FaceRenderer
from tempfile import TemporaryFile


def send_verts(verts: np.ndarray, conn: socket.socket):
    dump = pickle.dumps(verts)
    conn.sendall(dump)
    conn.sendall(b"ENDMSG")


def entry():

    HOST = sys.argv[1].encode("ascii")
    PORT = int(sys.argv[2])

    print("connecting to %s:%d" % (HOST, PORT), end="... ")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))
    print("connected")

    verts = np.zeros((468, 8), dtype=np.float32)

    verts[0][0:3] = [0, 1, 2]
    verts[1][0:3] = [3, 4, 5]
    verts[2][0:3] = [6, 7, 8]


    while True:
        # Idle until command received
        message = sock.recv(128).decode("utf-8")
        print("message: ", message)

        if message == "VERTS":
            print("Sending face vertices...")
            send_verts(verts, sock)
            continue

        elif message == "END":
            print("Terminating")
            break

    sock.close()

entry()