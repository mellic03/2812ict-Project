import glm as glm
import numpy as np
import ctypes
import os
import definitions as defs


dir_path = os.path.dirname(os.path.realpath(__file__))
lib = ctypes.cdll.LoadLibrary(dir_path + "/libgeom.so")


# CALCULATE_NORMALS ------------------------------------------------
lib.calculate_normals.restype = None
lib.calculate_normals.argtypes = [
    np.ctypeslib.ndpointer(ctypes.c_float, flags="C_CONTIGUOUS"),
    np.ctypeslib.ndpointer(ctypes.c_uint32, flags="C_CONTIGUOUS"),
    ctypes.c_size_t,
]
# ------------------------------------------------------------------


# LOAD_CFM ---------------------------------------------------------
lib.load_CFM.restype = None
lib.load_CFM.argtypes = [
    np.ctypeslib.ndpointer(ctypes.c_float, flags="C_CONTIGUOUS"),
    ctypes.c_size_t,
    ctypes.c_char_p,
    np.ctypeslib.ndpointer(ctypes.c_uint32, flags="C_CONTIGUOUS"),
    ctypes.c_size_t,
    ctypes.c_char_p
]
# ------------------------------------------------------------------


# LERP_VERTS -------------------------------------------------------
lib.lerp_verts.restype = None
lib.lerp_verts.argtypes = [
    np.ctypeslib.ndpointer(ctypes.c_float, flags="C_CONTIGUOUS"),
    np.ctypeslib.ndpointer(ctypes.c_float, flags="C_CONTIGUOUS"),
    ctypes.c_size_t,
    ctypes.c_float
]
# ------------------------------------------------------------------


def calculate_normals( vertices: np.ndarray, indices: np.ndarray ):
    lib.calculate_normals(vertices, indices, indices.size)


def load_CFM( vertices_path: str, indices_path: str ):

    # The number of indices is same as the number of
    # vertices because indexed rendering is used.

    vertices = np.ndarray((defs.FACE_NUM_FLOATS,),  dtype=np.float32)
    indices  = np.ndarray((defs.FACE_NUM_INDICES,), dtype=np.uint32)

    vpath = vertices_path.encode('utf-8')
    ipath = indices_path.encode('utf-8')

    lib.load_CFM(
        vertices,   vertices.size,  vpath,
        indices,    indices.size,   ipath
    )

    vertices = vertices.reshape(defs.FACE_NUM_VERTS, 8)
    return vertices, indices



def lerp_verts( verts0: np.ndarray, verts1: np.ndarray, alpha ):
    lib.lerp_verts(verts0, verts1, verts0.shape[0], alpha)

