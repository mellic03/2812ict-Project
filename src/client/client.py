
import glm as glm
import numpy as np
import ctypes
import os
import sys
import idk


dir_path = os.path.dirname(os.path.realpath(__file__))
lib = ctypes.cdll.LoadLibrary(dir_path + "/libclient.so")



lib.client_update_vertices.restype = None
lib.client_update_vertices.argtypes = [
    np.ctypeslib.ndpointer(ctypes.c_float, flags="C_CONTIGUOUS")
]


lib.client_get_vertices.restype = None
lib.client_get_vertices.argtypes = [
    np.ctypeslib.ndpointer(ctypes.c_float, flags="C_CONTIGUOUS"),
    ctypes.c_int
]


lib.client_get_userid.restype = ctypes.c_int
lib.client_get_userid.argtypes = [

]


lib.client_init.restype = None
lib.client_init.argtypes = [
    ctypes.c_char_p,
    ctypes.c_uint16
]


def update_vertices( vertices: np.ndarray ):
    lib.client_update_vertices(vertices)


def get_vertices( vertices: np.ndarray, userid: int ):
    lib.client_get_vertices(vertices, userid)


def get_userid( ):
    return lib.client_get_userid()


def init( hostname: str, port ):
    return lib.client_init(ctypes.c_char_p(hostname), port)






