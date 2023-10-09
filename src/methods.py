from OpenGL.GL import *
import glm
import idk
import math
import numpy as np
import cv2 as cv



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


# Methods related to monocular depth estimation
# ---------------------------------------------------------------------------------------------- 
def pixel_dist_to_real_dist( d, p, k ) -> float:
    """
    Given a known real-world distance `d` and it's corresponding distance in pixels `p`,
    estimate the real-world distance corresponding to the pixel distance `k`.
    This assumes both objects are the same distance from the camera.
    """
    return (k / p) * d


def pixel_dist_to_real_depth( pixel_focal_length, pixel_dist, real_dist ) -> float:
    """Convert"""

    return (pixel_focal_length * real_dist) / pixel_dist



def estimate_scaled_focal_length( real_depth_mm, real_dist_mm, measured_dist_pxl ) -> float:
    """
        Estimate the pixel-scaled focal length of the camera by comparing a real distance
        `real_dist_mm` to the measured distance in pixels `measured_dist_pxl`.
        This assumes the points used for each distance are all `real_depth_mm` millimetres from
        the camera.
    """
    return (real_depth_mm * measured_dist_pxl) / real_dist_mm


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
# ---------------------------------------------------------------------------------------------- 



# Methods related to hand and face orientation
# ---------------------------------------------------------------------------------------------- 

def joint_matrix( p1: glm.vec3, p2: glm.vec3 ) -> glm.mat4:

    dist = glm.distance(p1, p2)

    T: glm.mat4 = glm.translate(p1)
    R: glm.mat4 = glm.inverse(glm.lookAt(p1, p2, glm.vec3(0, 1, 0)))
    S: glm.mat4 = glm.scale(glm.vec3(0.03, 0.03, 2*dist))

    return T * R * S


def estimate_hand_orientation( landmarks3D: np.ndarray ) -> glm.mat4:

    lms = landmarks3D

    p0  = glm.vec3(lms[0])
    p5  = glm.vec3(lms[5])
    p17 = glm.vec3(lms[17])

    palm_dir = glm.normalize(glm.cross(p17 - p0, p5 - p0))
    side_dir = glm.normalize(p17 - p5)
    up_dir   = glm.normalize(glm.cross(side_dir, palm_dir))

    rotation = glm.mat4(1.0)
    rotation[0] = glm.vec4(side_dir,  0)
    rotation[1] = glm.vec4(up_dir,    0)
    rotation[2] = glm.vec4(-palm_dir, 0)

    return rotation


def derotate_hand( landmarks3D: np.ndarray ) -> list[glm.vec3]:

    p0  = landmarks3D[0]
    p5  = landmarks3D[5]
    p17 = landmarks3D[17]

    rotation = glm.inverse(estimate_hand_orientation(landmarks3D))

    derotated = [ ]
    for point in landmarks3D:
        derotated.append( glm.vec3(rotation * glm.vec4(point, 1.0)) )

    return derotated


def estimate_face_direction(leye, reye, philtrum) -> glm.vec3:
    direction = glm.normalize(glm.cross(philtrum - reye, philtrum - leye))
    return direction
# ---------------------------------------------------------------------------------------------- 


# Methods related to hand gesture recognition
# ---------------------------------------------------------------------------------------------- 
def hand_is_grabbing( landmarks3D: np.ndarray ) -> bool:

    lms = derotate_hand(landmarks3D)

    x4  = math.fabs(lms[ 4].x)
    x5  = math.fabs(lms[ 5].x)
    x17 = math.fabs(lms[17].x)

    xmax = max(x5, x17)
    xmin = min(x5, x17)

    y0  = lms[ 0].y
    y5  = lms[ 5].y
    y8  = lms[ 8].y
    y9  = lms[ 9].y
    y12 = lms[12].y
    y13 = lms[13].y
    y16 = lms[16].y
    y17 = lms[17].y
    y20 = lms[20].y

    # Add ymin to all y values making all values positive.
    # math.fabs() alone will not work: [0.5, 0.3, -0.4] --> [0.5, 0.4, 0.3]
    ymin = min([y0, y5, y8, y9, y12, y13, y16, y17, y20])

    y0  += math.fabs(ymin)
    y5  += math.fabs(ymin)
    y8  += math.fabs(ymin)
    y9  += math.fabs(ymin)
    y12 += math.fabs(ymin)
    y13 += math.fabs(ymin)
    y16 += math.fabs(ymin)
    y17 += math.fabs(ymin)
    y20 += math.fabs(ymin)


    c0 = y0 > y8  > y5
    c1 = y0 > y12 > y9
    c2 = y0 > y16 > y13
    c3 = y0 > y20 > y17
    c4 = xmin < x4 < xmax

    return c0 and c1 and c2 and c3
# ---------------------------------------------------------------------------------------------- 



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

