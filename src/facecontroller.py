from OpenGL.GL import *
import glm as glm
import idk
from sdl2 import *
import configparser
from face_vertices import *
from facerenderer import FaceRenderer

import methods
import definitions as defs


LM_LEFT_BROW   = 223
LM_RIGHT_BROW  = 443
LM_CENTER_BROW = 168
LM_PHILTRUM    = 164


def collect_avg( vertices, indices ) -> glm.vec3:
    avg = glm.vec3(0.0)
    count = 0
    for pair in indices:
        avg += glm.vec3(
            vertices[pair[1]][0],
            vertices[pair[1]][1],
            vertices[pair[1]][2],
        )
        count += 1
    return avg / count




class FaceController():

    def __reload_ini(self) -> None:
        self.config.read(self.configpath)
        tconfig = self.config["translation"]
        yawconfig   = self.config["yaw"]
        pitchconfig = self.config["pitch"]
        eyeconfig   = self.config["eyes"]

        self.transconfig = {
            "scale": glm.vec3([float(f) for f in tconfig["scale"].strip('\n').split(',')])
        }
        self.yawconfig = {
            "temp_strength":  float(yawconfig["temp_strength"]),
            "perm_strength":  float(yawconfig["perm_strength"]),
            "perm_threshold": float(yawconfig["perm_threshold"]),
            "direction":      glm.vec3(1.0, 0.0, 0.0)
        }
        self.pitchconfig = {
            "temp_strength":  float(pitchconfig["temp_strength"]),
            "perm_strength":  float(pitchconfig["perm_strength"]),
            "perm_threshold": float(pitchconfig["perm_threshold"]),
            "direction":      glm.vec3(0.0, 1.0, 0.0)
        }
        self.eyeconfig = {
            "lerp_alpha":     float(eyeconfig["lerp_alpha"]),
            "temp_strength":  float(eyeconfig["temp_strength"]),
        }
        self.measurements = {
            "IPD_mm":      float(self.config["measurements"]["inter-pupillary-distance-mm"]),
            "BPD_mm":      float(self.config["measurements"]["brow-philtrum-distance-mm"])
        }



    def __init__(self, configpath) -> None:
        self.configpath = configpath
        self.config = configparser.ConfigParser()
        self.__reload_ini()

        self.__philtrum    = glm.vec3(0.0)
        self.__front       = glm.vec3(0.0)
        self.__translation = glm.vec3(0.0)
        self.__depth       = 0.0


    def philtrum(self) -> glm.vec3:
        return self.__philtrum


    def front(self) -> glm.vec3:
        return self.__front


    def translation(self) -> glm.vec3:
        return self.__translation
    

    def getDepth(self) -> float:
        return self.__depth


    __last_leye_x = 0.0
    def __compute_orientation_leye( self, fh ) -> glm.vec3:
        xtop = fh.vertices[386][0]
        xbot = fh.vertices[374][0]

        xmax = max(xtop, xbot)
        xmin = min(xtop, xbot)

        xmax -= xmin
        eye_x = fh.iris_l_pos.x - xmin

        # eye_x = (eye_x / xmax) - 0.5
        # normal = (glm.vec3(eye_x, 0.0, 0.0))
        normal = (glm.vec3(1, 0.0, 0.0))

        return normal


    __last_reye_x = 0.0
    def __compute_orientation_reye( self, fh ) -> glm.vec3:
        xtop = fh.vertices[159][0]
        xbot = fh.vertices[145][0]

        xmax = max(xtop, xbot)
        xmin = min(xtop, xbot)

        xmax -= xmin
        eye_x = fh.iris_r_pos.x - xmin

        # eye_x = (eye_x / xmax) - 0.5
        # normal = (glm.vec3(eye_x, 0.0, 0.0))
        normal = (glm.vec3(1, 0.0, 0.0))

        return normal


    __delta_eye = glm.vec3(0.0)
    __delta_eye2 = glm.vec3(0.0)
    __last_eye = glm.vec3(0.0)
    def __camera_compute_orientation_eyes( self, fh ) -> glm.vec3:
        normal = self.__compute_orientation_leye(fh) + self.__compute_orientation_reye(fh)
        self.__last_eye = glm.lerp(self.__last_eye, normal, self.eyeconfig["lerp_alpha"])

        self.__delta_eye = self.__last_eye - self.__delta_eye2
        self.__delta_eye2 = self.__last_eye

        return self.__last_eye


    def __camera_compute_orientation( self, fh ) -> glm.vec3:
        philtrum = glm.vec3(fh.vertices[164][0:4])
        left_brow = glm.vec3(fh.vertices[223][0:4])
        right_brow = glm.vec3(fh.vertices[443][0:4])

        normal = glm.normalize(glm.cross(right_brow-philtrum, left_brow-philtrum))

        self.__philtrum = philtrum

        return normal


    def __camera_compute_position( self, vertices ) -> glm.vec3:
        leye_avg = collect_avg(vertices, FACEMESH_LEFT_EYE)
        reye_avg = collect_avg(vertices, FACEMESH_RIGHT_EYE)
        return glm.vec3(0.0) # (leye_avg + reye_avg) / 2.0


    def __camera_get_rot( self, normal, config ) -> glm.vec3:
        temp_strength  = config["temp_strength"]
        perm_strength  = config["perm_strength"]
        perm_threshold = config["perm_threshold"]
        direction      = config["direction"]
        dot            = glm.dot(normal, direction)
        
        temp_rot = temp_strength * glm.dot(self.__delta_rot, direction)
        perm_rot = 0

        if dot < -perm_threshold:
            perm_rot = perm_strength * glm.clamp(dot+perm_threshold, -1, 0)
        elif dot > +perm_threshold:
            perm_rot = perm_strength * glm.clamp(dot-perm_threshold,  0, 1)

        # If inside threshold
        elif dot < 0:
            temp_rot += self.eyeconfig["temp_strength"] * glm.dot(self.__delta_eye, direction)
        elif dot > 0:
            temp_rot += self.eyeconfig["temp_strength"] * glm.dot(self.__delta_eye, direction)

        return temp_rot + perm_rot


    __delta_rot = glm.vec3(0.0)
    __last_yaw   = 0
    __last_pitch = 0
    def __camera_apply_orientation( self, cam: idk.Camera, facenormal: glm.vec3 ) -> None:
        normal    = glm.normalize(facenormal)
        alpha = float(self.config["rotation"]["lerp_alpha"])

        self.__delta_rot = normal - self.__delta_rot

        yaw   = self.__camera_get_rot(normal, self.yawconfig)
        pitch = self.__camera_get_rot(normal, self.pitchconfig)

        self.__last_yaw = glm.lerp(self.__last_yaw, yaw, alpha)
        self.__last_pitch = glm.lerp(self.__last_pitch, pitch, alpha)

        cam.yaw(self.__last_yaw)
        cam.pitch(self.__last_pitch)

        self.__delta_rot = normal

    
    __delta_pos = glm.vec3(0.0)
    __last_pos  = glm.vec3(0.0)
    def __camera_apply_translation( self, cam: idk.Camera, position: glm.vec3 ) -> None:
        alpha = float(self.config["translation"]["lerp_alpha"])
        scale = self.transconfig["scale"]

        self.__delta_pos = position - self.__delta_pos
        self.__last_pos = glm.lerp(self.__last_pos, self.__delta_pos, alpha)

        cam.translate(glm.mul(self.__last_pos, scale))
        self.__delta_pos = position



    def update(self, fr: FaceRenderer, cam: idk.Camera) -> None:

        if fr.ready == False:
            return

        # Depth estimation
        #---------------------------------------------------------------------------------------
        lbrow = glm.vec2(fr.vertices[LM_LEFT_BROW][0:3])
        rbrow = glm.vec2(fr.vertices[LM_RIGHT_BROW][0:3])
        cbrow = glm.vec2(fr.vertices[LM_CENTER_BROW][0:3])
        philtrum_pos    = glm.vec2(fr.vertices[LM_PHILTRUM][0:3])

        # print(left_brow_pos, ", ", right_brow_pos)

        real_IPD = self.measurements["IPD_mm"]
        real_BPD = self.measurements["BPD_mm"]

        f = defs.FOCAL_LENGTH
        W = defs.IMG_W
        H = defs.IMG_H

        depth_IPD = methods.estimate_depth_mm(f, lbrow, rbrow,        real_IPD, W, H)
        depth_BPD = methods.estimate_depth_mm(f, cbrow, philtrum_pos, real_BPD, W, H)
        self.__depth = min([depth_IPD, depth_BPD]) / 1000.0

        # print("FACE:  %.2f,  %.2f" % (depth_IPD/1000, depth_BPD/1000))
        #---------------------------------------------------------------------------------------


        self.__front       = self.__camera_compute_orientation(fr)
        self.__translation = self.__camera_compute_position(fr.vertices)

        self.__camera_apply_orientation(cam, self.__front)
        self.__camera_apply_translation(cam, self.__translation)



    def onEvent( self, state, dtime ) -> None:

        if state[SDL_SCANCODE_F5]:
            self.__reload_ini()


