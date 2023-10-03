import glm


def estimate_depth_mm(pixel_focal_length, p1, p2, real_distance) -> float:
    """
        Estimate the distance to an object by comparing a pixel distance (p1, p2)
        to a real-world distance (real_distance). 
    """

    pixel_distance = glm.distance(p1, p2)
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

