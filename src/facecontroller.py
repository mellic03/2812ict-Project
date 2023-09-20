from OpenGL.GL import *
import glm as glm

import idk
from sdl2 import *

import numpy as np
import cv2 as cv
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import math

import configparser
import libgeometry as geom

from face_vertices import *

from facerenderer import FaceRenderer



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
        rotconfig   = self.config["rotation"]

        self.transconfig = {
            "scale": glm.vec3([float(f) for f in tconfig["scale"].strip('\n').split(',')])
        }
        self.yawconfig = {
            "temp_strength":  float(rotconfig["temp_yaw_strength"]),
            "perm_strength":  float(rotconfig["perm_yaw_strength"]),
            "perm_threshold": float(rotconfig["perm_yaw_threshold"]),
            "direction":      glm.vec3(1.0, 0.0, 0.0)
        }
        self.pitchconfig = {
            "temp_strength":  float(rotconfig["temp_pitch_strength"]),
            "perm_strength":  float(rotconfig["perm_pitch_strength"]),
            "perm_threshold": float(rotconfig["perm_pitch_threshold"]),
            "direction":      glm.vec3(0.0, 1.0, 0.0)
        }



    def __init__(self, configpath) -> None:
        self.configpath = configpath
        self.config = configparser.ConfigParser()
        self.__reload_ini()


    def __compute_orientation( self, vertices ) -> glm.vec3:
        leye_avg = collect_avg(vertices, FACEMESH_LEFT_EYE)
        reye_avg = collect_avg(vertices, FACEMESH_RIGHT_EYE)
        mouth_avg = collect_avg(vertices, FACEMESH_LIPS)
        normal = glm.normalize(glm.cross(leye_avg-mouth_avg, reye_avg-mouth_avg))
        return normal

    def __compute_position( self, vertices ) -> glm.vec3:
        leye_avg = collect_avg(vertices, FACEMESH_LEFT_EYE)
        reye_avg = collect_avg(vertices, FACEMESH_RIGHT_EYE)
        return (leye_avg + reye_avg) / 2.0


    def __camera_get_rot( self, normal, config ) -> None:
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

        return temp_rot + perm_rot


    __delta_rot = glm.vec3(0.0)
    __last_yaw   = 0
    __last_pitch = 0
    def __camera_lerp_orientation( self, cam: idk.Camera, normal: glm.vec3 ) -> None:
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
    def __camera_do_translation( self, cam: idk.Camera, position: glm.vec3 ) -> None:
        alpha = float(self.config["translation"]["lerp_alpha"])
        scale = self.transconfig["scale"]

        self.__delta_pos = position - self.__delta_pos
        self.__last_pos = glm.lerp(self.__last_pos, self.__delta_pos, alpha)

        cam.translate(glm.mul(self.__last_pos, scale))
        self.__delta_pos = position


    def update(self, fh: FaceRenderer, cam: idk.Camera) -> None:
        if fh.ready == False:
            return

        normal = self.__compute_orientation(fh.vertices)
        position = self.__compute_position(fh.vertices)

        self.__camera_lerp_orientation(cam, normal)
        self.__camera_do_translation(cam, position)

    def onEvent( self, state, dtime ) -> None:

        if state[SDL_SCANCODE_F5]:
            self.__reload_ini()


