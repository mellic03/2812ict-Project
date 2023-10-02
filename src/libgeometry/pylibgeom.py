
#
# Python implementations of the libgeometry methods
#
#
import glm as glm
import numpy as np
import ctypes
import definitions as defs



def load_CFM( vertices_path: str, indices_path: str ):

    vertices = np.ndarray((defs.FACE_NUM_FLOATS,),  dtype=np.float32)
    indices  = np.ndarray((defs.FACE_NUM_INDICES,), dtype=np.uint32)

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
                count += 3

            elif count == 8:
                count = 0

    i = 0
    with open(indices_path, "r") as fh:

        for line in fh:
            if line == "":
                continue

            inds = [int(ind) for ind in line.strip("\n").split(" ")]

            indices[i+0] = inds[0]
            indices[i+1] = inds[1]
            indices[i+2] = inds[2]

            i += 3

    vertices = vertices.reshape((defs.FACE_NUM_VERTS, 8))

    return vertices, indices


def glm_angle(u: glm.vec3, v: glm.vec3):
    return np.arccos(glm.dot(u, v) / (glm.length(u) * glm.length(v)))


def calculate_normals(vertices: np.ndarray, indices: np.ndarray):

    # Calculate normals
    # for i in range(0, indices.shape[0], 3):
    #     idx0 = indices[i+0]
    #     idx1 = indices[i+1]
    #     idx2 = indices[i+2]

    #     v0 = vertices[idx0]
    #     v1 = vertices[idx1]
    #     v2 = vertices[idx2]

    #     p0 = glm.vec3(v0[0], v0[1], v0[2])
    #     p1 = glm.vec3(v1[0], v1[1], v1[2])
    #     p2 = glm.vec3(v2[0], v2[1], v2[2])

    #     N = glm.normalize(glm.cross(p1-p0, p2-p0))

    #     theta0 = glm_angle(p1-p0, p2-p0)
    #     theta1 = glm_angle(p2-p1, p0-p1)
    #     theta2 = glm_angle(p0-p2, p1-p0)

    #     N0 = theta0 * N
    #     N1 = theta1 * N
    #     N2 = theta2 * N

    #     v0[3:6] = N0[0:4]
    #     v1[3:6] = N1[0:4]
    #     v2[3:6] = N2[0:4]


    # for i in range(0, indices.size):
    #     idx = indices[i]

    #     normal = glm.vec3(vertices[idx][3:6])
    #     normal = glm.normalize(normal)

    #     vertices[idx][3] = normal.x
    #     vertices[idx][4] = normal.y
    #     vertices[idx][5] = normal.z

    # for i in range(0, indices.size):
    #     idx = indices[i]

    #     vertices[idx][3] = 1.0
    #     vertices[idx][4] = 1.0
    #     vertices[idx][5] = 1.0
    return


def lerp_verts( verts0: np.ndarray, verts1: np.ndarray, alpha ):
    assert verts0.shape == verts1.shape, "verts0 and verts1 are of different shapes"

    for i in range(0, verts0.shape[0]):
        v0 = verts0[i]
        v1 = verts1[i]

        # v0[0] = alpha*v0[0] + (1.0-alpha)*v1[0]
        # v0[1] = alpha*v0[1] + (1.0-alpha)*v1[1]
        # v0[2] = alpha*v0[2] + (1.0-alpha)*v1[2]

        v0[0] = v1[0]
        v0[1] = v1[1]
        v0[2] = v1[2]

    

