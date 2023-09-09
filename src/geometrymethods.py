import glm as glm
import numpy as np
import ctypes
import os
import sys


def load_CPP_methods():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    lib = ctypes.cdll.LoadLibrary(dir_path + "/process_verts.so")


    METHODS = {  }

    __cpp_process_vertices = lib.process_vertices
    __cpp_process_vertices.restype = None
    __cpp_process_vertices.argtypes = [
        np.ctypeslib.ndpointer(ctypes.c_float, flags="C_CONTIGUOUS"),
        ctypes.c_size_t
    ]

    METHODS["process_vertices"] = __cpp_process_vertices
    return METHODS


def check_USE_CPP():
    if len(sys.argv) > 1 and sys.argv[1] == "USE_CPP":
        print("USE_CPP")
        return True

    print("USE_PYTHON")
    return False



ENV_USE_CPP = check_USE_CPP()
__CPP_METHODS = {  }

if ENV_USE_CPP:
    __CPP_METHODS = load_CPP_methods()



def python_process_vertices(arr: np.ndarray):

    vertices = arr

    # Calculate normals
    for i in range(0, vertices.size, 3*8):
        p0 = vertices[i+0*8 : i+0*8+3]
        p1 = vertices[i+1*8 : i+1*8+3]
        p2 = vertices[i+2*8 : i+2*8+3]

        p0 = glm.vec3(p0[0], p0[1], p0[2])
        p1 = glm.vec3(p1[0], p1[1], p1[2])
        p2 = glm.vec3(p2[0], p2[1], p2[2])

        normal = glm.normalize(glm.cross(p1-p0, p2-p0))
        vertices[i+0*8+4 : i+0*8+7] = [normal.x, normal.y, normal.z]
        vertices[i+1*8+4 : i+1*8+7] = [normal.x, normal.y, normal.z]
        vertices[i+2*8+4 : i+2*8+7] = [normal.x, normal.y, normal.z]




def process_vertices(arr: np.ndarray):
    if ENV_USE_CPP:
        __CPP_METHODS["process_vertices"](arr, arr.size)

    else:
        python_process_vertices(arr)
