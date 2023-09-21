
#
# Python implementations of the libgeometry methods
#
#
import glm as glm
import numpy as np
import ctypes
import definitions as defs




adj_normals = np.ndarray((defs.FACE_NUM_INDICES, defs.FACE_NUM_INDICES, 3))


def load_CFM( vertices_path: str, indices_path: str ):

    vertices = np.ndarray((defs.FACE_NUM_FLOATS), dtype=np.float32)
    indices  = np.ndarray((defs.FACE_NUM_INDICES), dtype=np.uint32)
    
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
                vertices[i+1] = 1.0
                vertices[i+2] = 1.0
                vertices[i+3] = 1.0
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

    vertices = vertices.reshape((defs.FACE_NUM_VERTS, 8))

    return vertices, indices


def glm_angle(u: glm.vec3, v: glm.vec3):
    return np.arccos(glm.dot(u, v) / (glm.length(u) * glm.length(v)))


def calculate_normals(vertices: np.ndarray, indices: np.ndarray):

    # for i in range(0, len(adj_normals)):
    #     adj_normals[i] = np.ndarray((NUM_INDICES, 3))

    # Calculate normals
    for i in range(0, indices.shape[0], 3):
        idx0 = indices[i+0]
        idx1 = indices[i+1]
        idx2 = indices[i+2]

        v0 = vertices[idx0]
        v1 = vertices[idx1]
        v2 = vertices[idx2]

        p0 = glm.vec3(v0[0], v0[1], v0[2])
        p1 = glm.vec3(v1[0], v1[1], v1[2])
        p2 = glm.vec3(v2[0], v2[1], v2[2])

        N = glm.normalize(glm.cross(p1-p0, p2-p0))

        theta0 = glm_angle(p1-p0, p2-p0)
        theta1 = glm_angle(p2-p1, p0-p1)
        theta2 = glm_angle(p0-p2, p1-p0)


        N0 = theta0 * N
        N1 = theta1 * N
        N2 = theta2 * N


    for i in range(0, indices.size):
        idx = indices[i]

        normal = [ 0.0, 0.0, 1.0 ]

        for n in adj_normals[idx]:
            normal[0] += n[0]
            normal[1] += n[1]
            normal[2] += n[2]

        vertices[idx][0] = normal[0]
        vertices[idx][1] = normal[1]
        vertices[idx][2] = normal[2]



def lerp_verts( verts0: np.ndarray, verts1: np.ndarray, alpha ):
    assert verts0.shape == verts1.shape, "verts0 and verts1 are of different shapes"

    for i in range(0, verts0.shape[0]):
        v0 = verts0[i]
        v1 = verts1[i]

        v0[0] = alpha*v0[0] + (1.0-alpha)*v1[0]
        v0[1] = alpha*v0[1] + (1.0-alpha)*v1[1]
        v0[2] = alpha*v0[2] + (1.0-alpha)*v1[2]


    

