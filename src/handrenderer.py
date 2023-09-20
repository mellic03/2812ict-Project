
from OpenGL.GL import *
import glm as glm

import idk

import threading
import numpy as np
import cv2 as cv
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import math

import configparser
import libgeometry as geom


# Data points for a polynomial regression
x = [300, 245, 200, 170, 145, 130, 112, 103, 93, 87, 80, 75, 70, 67, 62, 59, 57]
y = [20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100]
coff = np.polyfit(x, y, 2)  # y = Ax^2 + Bx + C

JOINT_LISTS = [
    [0, 1, 2, 3, 4],
    [1, 5],
    [0, 9],
    [0, 13],
    [0, 5, 6, 7, 8],
    [5, 9],
    [9, 10, 11, 12],
    [9, 13],
    [13, 14, 15, 16],
    [13, 17],
    [0, 17, 18, 19, 20]
]

FINGERTIPS = [ 4, 8, 12, 16, 20 ]

DIST_0_5  = 65
DIST_5_17 = 70
DIST_0_17 = 90

WRIST = 0
INDEX_FINGER_MCP = 5
PINKY_MCP = 17




def x_alignment(x0, y0, x1, y1):
    """ Return a value between 0-1 representing how aligned two point are on the x-axis"""
    dir = glm.normalize(glm.vec2(x1, y1) - glm.vec2(x0, y0))
    return glm.abs(dir.x)



class HandRenderer:

    def __init__(self, configpath) -> None:
        self.wrist = [0, 0, 0]
        self.wrist2 = [0, 0, 0]

        config = configparser.ConfigParser()
        config.read(configpath)

        self.hand_color = glm.vec3(
            float(config["color"]["hand_r"]) / 255.0,
            float(config["color"]["hand_g"]) / 255.0,
            float(config["color"]["hand_b"]) / 255.0
        )

        self.hand_shader = idk.compileShaderProgram("src/shaders/", "general.vs", "hands/hands.fs")

        uvsphere = idk.Model()
        unit = idk.Model()
        
        self.uvsphere_h = uvsphere.loadOBJ(b"models/icosphere.obj")
        self.unit_h = unit.loadOBJ(b"models/cylinder.obj")

        self.lms = np.zeros((21, 3), dtype=np.float32)
        self.lms2 = np.zeros((21, 3), dtype=np.float32)
        self.wlms = np.zeros((21, 3), dtype=np.float32)
        self.wlms2 = np.zeros((21, 3), dtype=np.float32)

        self.idx = 0



    def dist_estimate(self, j1_enum, j2_enum, real, res_x, res_y):

        lms = self.lms
        if self.idx == 1:
            lms = self.lms2

        x0 = lms[j1_enum][0]
        y0 = lms[j1_enum][1]
        
        x1 = lms[j2_enum][0]
        y1 = lms[j2_enum][1]

        aspect = res_x / res_y
        y0p = y0 / aspect
        y1p = y1 / aspect

        pixel_dist = np.sqrt((x0-x1)**2 + (y0p-y1p)**2)
        return res_x / (real*pixel_dist)




    def __draw_joint_list(self, joint_list, cam: idk.Camera) -> None:
        
        wrist = self.wrist
        if self.idx == 1:
            wrist = self.wrist2

        for i in range(0, len(joint_list)-1):

            a = self.wlms[joint_list[i]]
            b = self.wlms[joint_list[i+1]]

            if self.idx == 1:
                a = self.wlms2[joint_list[i]]
                b = self.wlms2[joint_list[i+1]]

            pos_u = glm.vec3(wrist[0]+a[0]+0.5, wrist[1]+a[1]+0.5, wrist[2]+a[2])
            pos_v = glm.vec3(wrist[0]+b[0]+0.5, wrist[1]+b[1]+0.5, wrist[2]+b[2])

            dist = glm.distance(pos_v, pos_u)

            pos_scale = glm.scale(glm.vec3(0.03, 0.03, 2*dist))
            pos_rot = glm.inverse(glm.lookAt(pos_u, pos_v, glm.vec3(0.0, 1.0, 0.0)))
            pos_trans = glm.translate(pos_u)
            transform = glm.inverse(cam.viewMatrix()) * pos_trans * pos_rot * pos_scale

            # Digits
            idk.setmat4(self.hand_shader, "un_model", transform)
            idk.setvec3(self.hand_shader, "un_color", glm.vec3(1.0, 1.0-(i*0.25), 1.0-(i*0.25)))
            idk.drawVertices(self.unit_h)

            # Knuckles
            pos_scale = glm.scale(glm.vec3(0.03))
            pos_trans = glm.translate(pos_u)
            transform = glm.inverse(cam.viewMatrix()) * pos_trans * pos_rot * pos_scale
            idk.setmat4(self.hand_shader, "un_model", transform)
            idk.drawVertices(self.uvsphere_h)

            # Fingertips
            pos_scale = glm.translate(glm.vec3(0.0, 0.0, -dist)) * glm.scale(glm.vec3(0.03))
            pos_trans = glm.translate(pos_v)
            transform = pos_trans*pos_rot*pos_scale
            transform = glm.inverse(cam.viewMatrix()) * transform
            idk.setmat4(self.hand_shader, "un_model", transform)
            idk.drawVertices(self.uvsphere_h)


    def __draw(self, handDetector, handLms, whandLms, cam) -> None:

        img_w = handDetector.img.shape[1]
        img_h = handDetector.img.shape[0]
        aspect = img_w/img_h
        alpha1 = 0.0


        lms = self.lms
        wlms = self.wlms
        if self.idx == 1:
            lms = self.lms2
            wlms = self.wlms2

        new_landmarks = np.zeros(lms.shape, dtype=np.float32)
        geom.lmarks_to_np(handLms.landmark, new_landmarks, aspect)

        for i in range(0, lms.shape[0]):
            v0 = lms[i]
            v1 = new_landmarks[i]
            v0[0] = glm.lerp(v1[0], v0[0], alpha1)
            v0[1] = glm.lerp(v1[1], v0[1], alpha1)
            v0[2] = glm.lerp(v1[2], v0[2], alpha1)



        new_landmarks = np.zeros(wlms.shape, dtype=np.float32)
        geom.lmarks_to_np(whandLms.landmark, new_landmarks, aspect)

        for i in range(0, wlms.shape[0]):
            v0 = wlms[i]
            v1 = new_landmarks[i]
            v0[0] = glm.lerp(v1[0], v0[0], alpha1)
            v0[1] = glm.lerp(v1[1], v0[1], alpha1)
            v0[2] = glm.lerp(v1[2], v0[2], alpha1)


        dist0 = self.dist_estimate(WRIST,     INDEX_FINGER_MCP, DIST_0_5,  img_w, img_h)
        dist1 = self.dist_estimate(PINKY_MCP, INDEX_FINGER_MCP, DIST_5_17, img_w, img_h)
        dist2 = self.dist_estimate(PINKY_MCP, WRIST,            DIST_0_17, img_w, img_h)
        dist  = min([dist0, dist1, dist2])

        alpha2 = 0.5
        wrist = lms[0]
        scale = 5*(1.0 - dist/100)
        scale = glm.clamp(scale, 1, 10)
        # print(scale)

        if self.idx == 0:
            self.wrist = [
                glm.lerp(scale*wrist[0], self.wrist[0], alpha2),
                glm.lerp(scale*wrist[1], self.wrist[1], alpha2),
                glm.lerp(glm.clamp(-2.1 + (dist/50), -2.1, -0.2), self.wrist[2], alpha2)
            ]

        elif self.idx == 1:
            self.wrist2 = [
                glm.lerp(scale*wrist[0], self.wrist2[0], alpha2),
                glm.lerp(scale*wrist[1], self.wrist2[1], alpha2),
                glm.lerp(glm.clamp(-2.1 + (dist/50), -2.1, -0.2), self.wrist2[2], alpha2)
            ]

        for joint_list in JOINT_LISTS:
            self.__draw_joint_list(joint_list, cam)


    def draw(self, handDetector, cam: idk.Camera) -> None:
        results = handDetector.m_results
        if not results or not results.multi_hand_landmarks:
            return

        glUseProgram(self.hand_shader)
        idk.setmat4(self.hand_shader, "un_proj", cam.projection())
        idk.setmat4(self.hand_shader, "un_view", cam.viewMatrix())

        self.idx = 0
        results = handDetector.m_results
        if results and results.multi_hand_landmarks:
            for (handLms, whandLms) in zip(results.multi_hand_landmarks, results.multi_hand_world_landmarks):
                self.__draw(handDetector, handLms, whandLms, cam)
                self.idx += 1
