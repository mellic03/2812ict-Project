
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

DIST_0_5  = 1
DIST_5_17 = 1
DIST_0_17 = 1

CV_MP_HAND_LEFT  = False
CV_MP_HAND_RIGHT = True


class HandRenderer:

    def __init__(self, configpath) -> None:
        self.wrist = glm.vec3(0.0) # Origin of hand

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

        self.landmarks = np.zeros((21, 3), dtype=np.float32)
        self.landmarks2 = np.zeros((21, 3), dtype=np.float32)


    def __draw_joint_list(self, joint_list, cam: idk.Camera) -> None:
        
        wrist = self.wrist

        for i in range(0, len(joint_list)-1):
            a = self.landmarks2[joint_list[i]]
            b = self.landmarks2[joint_list[i+1]]

            SCALE = 1

            pos_u = glm.vec3(SCALE*(wrist[0]+a[0]), SCALE*(wrist[1]+a[1]), wrist[2] + SCALE*(a[2]))
            pos_v = glm.vec3(SCALE*(wrist[0]+b[0]), SCALE*(wrist[1]+b[1]), wrist[2] + SCALE*(b[2]))
            dist = glm.length(pos_v - pos_u)

            # Digits
            pos_scale = glm.translate(glm.vec3(0.0, 0.0, -dist)) * glm.scale(glm.vec3(0.03, 0.03, 2*dist))
            pos_rot = glm.inverse(glm.lookAt(pos_u, pos_v, glm.vec3(0.0, 1.0, 0.0)))
            pos_trans = glm.translate(pos_u + glm.vec3(0.0, 0.0, -0.4))
            transform = pos_trans*pos_rot*pos_scale
            # transform = glm.inverse(cam.viewMatrix()) * transform
            idk.setmat4(self.hand_shader, "un_model", transform)
            idk.setvec3(self.hand_shader, "un_color", glm.vec3(1.0, 1.0-(i*0.25), 1.0-(i*0.25)))
            idk.drawVertices(self.unit_h)

            # Knuckles
            pos_scale = glm.scale(glm.vec3(0.03))
            pos_trans = glm.translate(pos_u + glm.vec3(0.0, 0.0, -0.4))
            transform = pos_trans*pos_rot*pos_scale
            # transform = glm.inverse(cam.viewMatrix()) * transform
            idk.setmat4(self.hand_shader, "un_model", transform)
            idk.drawVertices(self.uvsphere_h)

            # Fingertips
            pos_scale = glm.translate(glm.vec3(0.0, 0.0, -dist)) * glm.scale(glm.vec3(0.03))
            pos_trans = glm.translate(pos_v + glm.vec3(0.0, 0.0, -0.4))
            transform = pos_trans*pos_rot*pos_scale
            # transform = glm.inverse(cam.viewMatrix()) * transform
            idk.setmat4(self.hand_shader, "un_model", transform)
            idk.drawVertices(self.uvsphere_h)



    def __draw(self, handDetector, handLms, whandLms, cam) -> None:

        img_w = handDetector.img.shape[1]
        img_h = handDetector.img.shape[0]
        alpha = 0.7


        new_landmarks = np.zeros(self.landmarks.shape, dtype=np.float32)
        geom.lmarks_to_np(handLms.landmark, new_landmarks, 1)

        for i in range(0, self.landmarks.shape[0]):
            v0 = self.landmarks[i]
            v1 = new_landmarks[i]
            v0[0] = alpha*v0[0] + (1.0-alpha)*v1[0]
            v0[1] = alpha*v0[1] + (1.0-alpha)*v1[1]
            v0[2] = alpha*v0[2] + (1.0-alpha)*v1[2]



        new_landmarks = np.zeros(self.landmarks2.shape, dtype=np.float32)
        geom.lmarks_to_np(whandLms.landmark, new_landmarks, 1)

        for i in range(0, self.landmarks2.shape[0]):
            v0 = self.landmarks2[i]
            v1 = new_landmarks[i]
            v0[0] = alpha*v0[0] + (1.0-alpha)*v1[0]
            v0[1] = alpha*v0[1] + (1.0-alpha)*v1[1]
            v0[2] = alpha*v0[2] + (1.0-alpha)*v1[2]



        x0 = self.landmarks[5][0]
        y0 = self.landmarks[5][1]
        x1 = self.landmarks[17][0]
        y1 = self.landmarks[17][1]
        pixel_dist1 = np.sqrt((x0-x1)**2 + (y0-y1)**2)

        x0 = self.landmarks[0][0]
        y0 = self.landmarks[0][1]
        x1 = self.landmarks[17][0]
        y1 = self.landmarks[17][1]
        pixel_dist2 = np.sqrt((x0-x1)**2 + (y0-y1)**2)


        A, B, C = coff
        hand_dist1 = A*pixel_dist1**2 + B*pixel_dist1 + C
        hand_dist2 = A*pixel_dist2**2 + B*pixel_dist2 + C

        hand_dist = min(hand_dist1, hand_dist2)
        hand_dist /= 100

        wrist = self.landmarks[0]
        self.wrist = [(wrist[0]), (wrist[1]), wrist[2] - 1.0 + hand_dist]

        for joint_list in JOINT_LISTS:
            self.__draw_joint_list(joint_list, cam)


    def draw(self, handDetector, cam: idk.Camera) -> None:
        results = handDetector.m_results
        if not results or not results.multi_hand_landmarks:
            return


        glUseProgram(self.hand_shader)
        idk.setmat4(self.hand_shader, "un_proj", cam.projection())
        idk.setmat4(self.hand_shader, "un_view", cam.viewMatrix())

        results = handDetector.m_results
        if results and results.multi_hand_landmarks:
            for (handLms, whandLms) in zip(results.multi_hand_landmarks, results.multi_hand_world_landmarks):
                self.__draw(handDetector, handLms, whandLms, cam)
