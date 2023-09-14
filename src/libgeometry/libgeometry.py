import glm as glm
import numpy as np
import ctypes
import os
import sys
import idk


def check_USE_CPP():
    if len(sys.argv) > 1 and sys.argv[1] == "USE_CPP":
        return True
    return False

USE_CPP = check_USE_CPP()


if USE_CPP:
    import libgeometry.cpplibgeom as __libgeom
    print("Using C++ libraries")
else:
    import libgeometry.pylibgeom as __libgeom
    print("Using Python libraries")






def calculate_normals(vertices: np.ndarray, indices: np.ndarray):
    __libgeom.calculate_normals(vertices, indices)


def load_CFM( vertices_path: str, indices_path: str ):
    vertices, indices = __libgeom.load_CFM(vertices_path, indices_path)
    return vertices, indices


def lmarks_to_np( landmarks, nparray: np.ndarray, aspect=1, posoffset=glm.vec3(0.0) ):

    for i in range(0, len(landmarks)):
        if i >= nparray.shape[0]:
            break
        v = landmarks[i]
        nparray[i][0] = aspect * (v.x-0.5) + posoffset.x
        nparray[i][1] = v.y-0.5 + posoffset.y
        nparray[i][2] = v.z + posoffset.z


def lerp_verts( verts0: np.ndarray, verts1: np.ndarray, alpha ):
    """
        Interpolate between verts0 and verts1, storing the results in verts0.
    """
    __libgeom.lerp_verts(verts0, verts1, alpha)