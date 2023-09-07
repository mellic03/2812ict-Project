
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


class CV_MP_Hand:

    def __init__(self) -> None:
        self.wrist = glm.vec3(0.0) # Origin of hand

        uvsphere = idk.Model()
        unit = idk.Model()
        
        self.uvsphere_h = uvsphere.loadOBJ(b"models/cube/", b"icosphere.obj", b"cube.mtl", b"container.png")
        self.unit_h = unit.loadOBJ(b"models/cube/", b"cylinder.obj", b"cube.mtl", b"container.png")

        pass

    def __draw_joint_list(self, joint_list, whandLms, shaderID, cam, ren) -> None:
        
        wrist = self.wrist
        
        for i in range(0, len(joint_list)-1):
            a = whandLms.landmark[joint_list[i]]
            b = whandLms.landmark[joint_list[i+1]]

            SCALE = 1

            pos_u = glm.vec3(SCALE*(wrist[0]+a.x), SCALE*(wrist[1]+a.y), wrist[2] + SCALE*(a.z))
            pos_v = glm.vec3(SCALE*(wrist[0]+b.x), SCALE*(wrist[1]+b.y), wrist[2] + SCALE*(b.z))
            dist = glm.length(pos_v - pos_u)

            pos_scale = glm.translate(glm.vec3(0.0, 0.0, -dist)) * glm.scale(glm.vec3(0.03, 0.03, 2*dist))
            pos_rot = glm.inverse(glm.lookAt(pos_u, pos_v, glm.vec3(0.0, 1.0, 0.0)))
            pos_trans = glm.translate(pos_u + glm.vec3(0.0, 0.0, -0.4))
            transform = pos_trans*pos_rot*pos_scale
            if cam.coupled:
                transform = glm.inverse(cam.viewMatrix()) * transform
            else:
                transform = glm.translate(cam.last_pos) * transform
            ren.setmat4(shaderID, "model", transform)
            ren.setvec3(shaderID, "un_color", glm.vec3(1.0, 1.0-(i*0.25), 1.0-(i*0.25)))
            ren.drawVertices(self.unit_h)

            # Knuckles
            pos_scale = glm.scale(glm.vec3(0.03))
            pos_trans = glm.translate(pos_u + glm.vec3(0.0, 0.0, -0.4))
            transform = pos_trans*pos_rot*pos_scale
            if cam.coupled:
                transform = glm.inverse(cam.viewMatrix()) * transform
            else:
                transform = glm.translate(cam.last_pos) * transform
            ren.setmat4(shaderID, "model", transform)
            ren.drawVertices(self.uvsphere_h)

            # Fingertips
            pos_scale = glm.translate(glm.vec3(0.0, 0.0, -dist)) * glm.scale(glm.vec3(0.03))
            pos_trans = glm.translate(pos_v + glm.vec3(0.0, 0.0, -0.4))
            transform = pos_trans*pos_rot*pos_scale
            if cam.coupled:
                transform = glm.inverse(cam.viewMatrix()) * transform
            else:
                transform = glm.translate(cam.last_pos) * transform
            ren.setmat4(shaderID, "model", transform)
            ren.drawVertices(self.uvsphere_h)


    def __draw(self, handDetector, handLms, whandLms, shaderID, cam, ren) -> None:

        img_w = handDetector.img.shape[1]
        img_h = handDetector.img.shape[0]

        x0 = handLms.landmark[5].x * img_w
        y0 = handLms.landmark[5].y * img_h
        x1 = handLms.landmark[17].x * img_w
        y1 = handLms.landmark[17].y * img_h
        pixel_dist1 = np.sqrt((x0-x1)**2 + (y0-y1)**2)

        x0 = handLms.landmark[0].x * img_w
        y0 = handLms.landmark[0].y * img_h
        x1 = handLms.landmark[17].x * img_w
        y1 = handLms.landmark[17].y * img_h
        pixel_dist2 = np.sqrt((x0-x1)**2 + (y0-y1)**2)

        A, B, C = coff
        hand_dist1 = A*pixel_dist1**2 + B*pixel_dist1 + C
        hand_dist2 = A*pixel_dist2**2 + B*pixel_dist2 + C

        hand_dist = min(hand_dist1, hand_dist2)
        hand_dist /= 100
        # print(hand_dist)

        wrist = handLms.landmark[0]
        self.wrist = [(wrist.x-0.5), (wrist.y-0.75), wrist.z - 1.0 + hand_dist]

        for joint_list in JOINT_LISTS:
            self.__draw_joint_list(joint_list, whandLms, shaderID, cam, ren)


    def draw(self, handDetector, shaderID, cam, ren: idk.Renderer) -> None:
        results = handDetector.m_results
        if results and results.multi_hand_landmarks:
            for (handLms, whandLms) in zip(results.multi_hand_landmarks, results.multi_hand_world_landmarks):
                self.__draw(handDetector, handLms, whandLms, shaderID, cam, ren)
