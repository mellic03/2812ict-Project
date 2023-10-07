from OpenGL.GL import *
import glm
import idk
import math
import numpy as np
import cv2 as cv



def img_undistort( img: np.ndarray, cam_mat: np.ndarray, dst_coef: np.ndarray ) -> np.ndarray:

    return cv.undistort(img, cam_mat, dst_coef)


# Attempts at improving hand detection.
# ---------------------------------------------------------------------------------------------- 
# def img_edge_enhancement( img: np.ndarray ) -> np.ndarray:

#     gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
#     lap = cv.Laplacian(gray, -1, ksize=5, scale=1, delta=0, borderType=cv.BORDER_DEFAULT)
#     lap = cv.cvtColor(lap, cv.COLOR_GRAY2BGR)

#     # lap = cv.resize(lap, (0, 0), fx=0.5, fy=0.5, interpolation=cv.INTER_LINEAR)
#     # lap = cv.GaussianBlur(lap, (7, 7), 0)

#     # lap = cv.resize(lap, (0, 0), fx=2, fy=2, interpolation=cv.INTER_LINEAR)
#     # lap = cv.GaussianBlur(lap, (3, 3), 0)

#     lap = np.uint8(lap / 2)

#     return img
# ---------------------------------------------------------------------------------------------- 


# Monocular depth estimation
# ----------------------------------------------------------------------------------------------
def estimate_depth_mm( pixel_focal_length, p1, p2, real_distance, W=1, H=1 ) -> float:
    """
        Estimate the distance to an object by comparing a pixel distance (p1, p2)
        to a real-world distance (real_distance). 

        Set W and H to the horizontal and vertical image resolution if using normalized
        coordinates.
    """

    x1 = p1.x * W
    x2 = p2.x * W

    y1 = p1.y * H
    y2 = p2.y * H

    pixel_distance = math.sqrt((x1 - x2)**2 + (y1 - y2)**2)
    depth = (pixel_focal_length * real_distance) / pixel_distance

    return depth


def estimate_face_direction(leye, reye, philtrum) -> glm.vec3:
    direction = glm.normalize(glm.cross(philtrum - reye, philtrum - leye))
    return direction


def joint_matrix( p1: glm.vec3, p2: glm.vec3 ) -> glm.mat4:

    dist = glm.distance(p1, p2)

    T: glm.mat4 = glm.translate(p1)
    R: glm.mat4 = glm.inverse(glm.lookAt(p1, p2, glm.vec3(0, 1, 0)))
    S: glm.mat4 = glm.scale(glm.vec3(0.03, 0.03, dist))

    return T * R * S


def derotate_hand( landmarks: list[glm.vec3] ) -> list[glm.vec3]:

    p0 = landmarks[0]
    p5 = landmarks[5]
    p17 = landmarks[17]

    front = glm.normalize(glm.cross(p0 - p5, p0 - p17))

    rot =  glm.mat4(1.0)

    derotated = [ ]

    for point in landmarks:
        derotated.append( glm.vec3(rot * glm.vec4(point)) )

    return derotated



def hand_is_grabbing( landmarks3D: np.ndarray ) -> bool:

    # Call derotate_hand(), creating a list of de-rotated 3D hand landmarks.
    # Then, evaluate thresholds.

    return False



def render_vector( pos: glm.vec3, dir: glm.vec3, color=glm.vec3(0), length: float = None ) -> None:
    """
        Render a representation of a direction vector `dir` located at `pos`.
    """
    
    scale = glm.vec3(0.02, 0.02, glm.length(dir))

    if length is not None:
        scale.z = length

    scale       = glm.scale(scale)
    rotation    = glm.inverse(glm.lookAt(pos, pos+dir, glm.vec3(0.0, -1.0, 0.0)))
    translation = glm.translate(pos)

    transform = translation * rotation * scale

    shader_id = idk.getProgram("plaincolor")

    glUseProgram(shader_id)
    idk.setvec3(shader_id, "un_color", color)
    idk.setmat4(shader_id, "un_model", transform)
    idk.drawVertices(idk.getPrimitive(idk.PRIMITIVE_CYLINDER))

