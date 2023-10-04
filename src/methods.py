from OpenGL.GL import *
import glm
import idk
import math
import np




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

    return False


def render_vector( pos: glm.vec3, dir: glm.vec3, color=glm.vec3(0), scale=None ) -> None:
    """
        Render a representation of a direction vector `dir` located at `pos`.
    """
    
    if scale is None:
        scale = glm.vec3(0.02, 0.02, glm.length(dir))

    scale       = glm.scale(scale)
    rotation    = glm.inverse(glm.lookAt(pos, pos+dir, glm.vec3(0.0, -1.0, 0.0)))
    translation = glm.translate(pos)

    transform = translation * rotation * scale

    shader_id = idk.getProgram("plaincolor")

    glUseProgram(shader_id)
    idk.setvec3(shader_id, "un_color", color)
    idk.setmat4(shader_id, "un_model", transform)
    idk.drawVertices(idk.getPrimitive(idk.PRIMITIVE_CYLINDER))

