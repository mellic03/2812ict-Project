import glm as glm
import numpy as np
import ctypes
import os
import sys
import idk


def load_CPP_methods():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    lib = ctypes.cdll.LoadLibrary(dir_path + "/libgeom.so")

    METHODS = {  }

    lib.calculate_normals.restype = None
    lib.calculate_normals.argtypes = [
        np.ctypeslib.ndpointer(ctypes.c_float, flags="C_CONTIGUOUS"),
        np.ctypeslib.ndpointer(ctypes.c_uint32, flags="C_CONTIGUOUS"),
        ctypes.c_size_t,
    ]
    METHODS["calculate_normals"] = lib.calculate_normals

    lib.load_CFM.restype = None
    lib.load_CFM.argtypes = [
        np.ctypeslib.ndpointer(ctypes.c_float, flags="C_CONTIGUOUS"),
        ctypes.c_size_t,
        ctypes.c_char_p,
        np.ctypeslib.ndpointer(ctypes.c_uint32, flags="C_CONTIGUOUS"),
        ctypes.c_size_t,
        ctypes.c_char_p
    ]
    METHODS["load_CFM"] = lib.load_CFM


    return METHODS


def check_USE_CPP():
    if len(sys.argv) > 1 and sys.argv[1] == "USE_CPP":
        print("USE_CPP")
        return True

    print("USE_PYTHON")
    return False



__USE_CPP = check_USE_CPP()
__CPP_METHODS = {  }

if __USE_CPP:
    __CPP_METHODS = load_CPP_methods()



def python_calculate_normals(arr: np.ndarray):

    vertices = arr.tolist()

    # Calculate normals
    for i in range(0, len(vertices), 3*8):
        p0 = vertices[i+0*8 : i+0*8+3]
        p1 = vertices[i+1*8 : i+1*8+3]
        p2 = vertices[i+2*8 : i+2*8+3]

        p0 = glm.vec3(p0[0], p0[1], p0[2])
        p1 = glm.vec3(p1[0], p1[1], p1[2])
        p2 = glm.vec3(p2[0], p2[1], p2[2])

        normal = glm.normalize(glm.cross(p1-p0, p2-p0))
        vertices[i+0*8+3 : i+0*8+6] = [0.0, 0.0, -1.0] # [normal.x, normal.y, normal.z]
        vertices[i+1*8+3 : i+1*8+6] = [0.0, 0.0, -1.0] # [normal.x, normal.y, normal.z]
        vertices[i+2*8+3 : i+2*8+6] = [0.0, 0.0, -1.0] # [normal.x, normal.y, normal.z]




def calculate_normals(vertices: np.ndarray, indices: np.ndarray):
    if __USE_CPP:
        __CPP_METHODS["calculate_normals"](vertices, indices, indices.size)

    else:
        python_calculate_normals(vertices)



NUM_INDICES = 2640


def python_load_CFM( vertices_path: str, indices_path: str ):
    NUM_FLOATS  = (2340 // 5) * 8

    vertices = np.ndarray((NUM_FLOATS,),  dtype=np.float32)
    indices  = np.ndarray((NUM_INDICES,),  dtype=np.uint32)
    
    count = 0
    i = 0
    with open(vertices_path, "r") as fh:
        for line in fh:
            if line == "\n":
                continue
            vertices[i] = float(line.strip("\n"))
            i += 1
            count += 1

            if count == 3:
                vertices[i+1] = 0.0
                vertices[i+2] = 0.0
                vertices[i+3] = -1.0
                i += 3
                count = 6

            elif count == 8:
                count = 0

    i = 0
    with open(indices_path, "r") as fh:
        for line in fh:
            if line == "\n":
                continue
            indices[i] = int(line.strip("\n"))
            i += 1

    return vertices, indices



def load_CFM( vertices_path: str, indices_path: str ):

    """ Load the MediaPipe canonical face model.\n
        Returns (vertices, indices)
    """

    # The number of indices is same as the number of
    # vertices because indexed rendering is used.
    NUM_FLOATS  = (2340 // 5) * 8

    if __USE_CPP:
        vertices = np.ndarray((NUM_FLOATS,),  dtype=np.float32)
        indices  = np.ndarray((NUM_INDICES,), dtype=np.uint32)

        vpath = vertices_path.encode('utf-8')
        ipath = indices_path.encode('utf-8')

        __CPP_METHODS["load_CFM"](
            vertices,   vertices.size,  vpath,
            indices,    indices.size,   ipath
        )
        return vertices, indices

    else:
        vertices, indices = python_load_CFM(vertices_path, indices_path)
        return vertices, indices
