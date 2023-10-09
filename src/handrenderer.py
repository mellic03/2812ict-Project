
from OpenGL.GL import *
import glm as glm

import idk

import numpy as np
from google.protobuf.json_format import MessageToDict
import math

import configparser
import libgeometry as geom

import definitions as defs
import methods


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



class HandRenderer:

    def __reload_ini(self, configpath) -> None:
        config = configparser.ConfigParser()
        config.read(configpath)

        self.base_color = glm.vec3([
            float(f)/255 for f in config["default color"]["base"].strip('\n').split(',')
        ])
        self.tip_color = glm.vec3([
            float(f)/255 for f in config["default color"]["fingertips"].strip('\n').split(',')
        ])
        self.grab_base_color = glm.vec3([
            float(f)/255 for f in config["grab color"]["base"].strip('\n').split(',')
        ])
        self.grab_tip_color = glm.vec3([
            float(f)/255 for f in config["grab color"]["fingertips"].strip('\n').split(',')
        ])


    def __init__(self, configpath) -> None:

        self.__ready = False

        self.__reload_ini(configpath)
        self.shader = idk.compileShaderProgram("src/shaders/", "general.vs", "hands/hands.fs")

        self.lms       = np.zeros((21, 3), dtype=np.float32)
        self.wlms      = np.zeros((21, 3), dtype=np.float32)
        self.lms_prev  = np.copy(self.wlms)
        self.wlms_prev = np.copy(self.wlms)

        self.center     = glm.vec3(0)
        self.center_raw = glm.vec3(0)
        self.center_raw_prev = glm.vec3(0)

        self.rot_mat   = glm.mat4(1)
        self.trans_mat = glm.mat4(1)
        self.__depth   = 0.0

    
    def setRotation(self, rot: glm.mat4 ) -> None:
        self.rot_mat = rot


    def setTranslation(self, trans: glm.mat4 ) -> None:
        self.trans_mat = trans


    def depthCorrection(self, desired_depth) -> None:
        self.__depth = desired_depth


    def calculateDepth(self) -> float:

        if self.__ready == False:
            return 1

        p00 = glm.vec2(self.lms[0][0:3])
        p05 = glm.vec2(self.lms[5][0:3])
        p17 = glm.vec2(self.lms[17][0:3])

        f = defs.FOCAL_LENGTH
        W = defs.IMG_W
        H = defs.IMG_H

        depth0 = methods.estimate_depth_mm(f, p00, p05, defs.DIST_0_5_mm,  W, H)
        depth1 = methods.estimate_depth_mm(f, p00, p17, defs.DIST_0_17_mm, W, H)
        depth2 = methods.estimate_depth_mm(f, p05, p17, defs.DIST_5_17_mm, W, H)

        depth_mm = min([depth0, depth1, depth2])
        depth_m  = depth_mm / 1000.0

        return depth_m


    # Convert landmarks to numpy array and add wrist position to all other landmarks
    def __preprocess_vertices(self, cam, handLms, whandLms) -> None:

        self.lms_prev  = np.copy(self.lms)
        self.wlms_prev = np.copy(self.wlms)

        self.lms  = geom.lmarks_to_np(handLms.landmark, self.lms, 1)
        self.wlms = geom.lmarks_to_np(whandLms.landmark, self.wlms, 1, glm.vec2(0.0))


        pos_ndc = glm.vec3(self.lms[0][0], self.lms[0][1], self.__depth)
        # print("%.2f,  %.2f" % (pos_ndc.x, pos_ndc.y))

        viewspace = methods.ndc_to_viewspace(pos_ndc, cam.projection())
        viewspace.xy *= -1
        # print("%.2f,  %.2f\n" % (viewspace.x, viewspace.y))


        self.center_raw_prev = glm.vec3(self.center_raw)

        self.center_raw = glm.vec3(
            glm.lerp(self.lms[0][0],  self.center_raw.x, 0.8),
            glm.lerp(self.lms[0][1],  self.center_raw.y, 0.8),
            glm.lerp(self.__depth,    self.center_raw.z, 0.8)
        )

        self.center = glm.vec3(
            glm.lerp(2*viewspace.x, self.center[0], 0.8),
            glm.lerp(2*viewspace.y, self.center[1], 0.8),
            glm.lerp(self.__depth,  self.center[2], 0.8)
        )

        # Add center position to all other positions
        # --------------------------------------------------------------------------------------
        for i in range(0, len(self.wlms)):
            self.wlms[i][0] += self.center.x
            self.wlms[i][1] += self.center.y
            self.wlms[i][2] += self.center.z
        # --------------------------------------------------------------------------------------



    def __draw_joint_list(self, joint_list, cam: idk.Camera) -> None:

        for i in range(0, len(joint_list)-1):

            pos_u = glm.vec3(self.wlms[joint_list[i+0]])
            pos_v = glm.vec3(self.wlms[joint_list[i+1]])

            dist = glm.distance(pos_v, pos_u)

            scale        = glm.scale(glm.vec3(0.03, 0.03, 2*dist))
            joint_matrix = methods.joint_matrix(pos_u, pos_v)
            transform    = self.trans_mat * self.rot_mat * joint_matrix * scale

            color = glm.lerp(self.base_color, self.tip_color, i/2)
            # if self.grabbing:
            #     color = glm.lerp(self.grab_base_color, self.grab_tip_color, i/2)
            idk.setvec3(self.shader, "un_color", color)

            # Digits
            idk.setmat4(self.shader, "un_model", transform)
            idk.drawVertices(idk.getPrimitive(idk.PRIMITIVE_CYLINDER))

            # # Knuckles
            # pos_scale = glm.scale(glm.vec3(0.03))
            # pos_trans = glm.translate(pos_u)
            # local_transform = pos_trans * pos_rot * pos_scale
            # global_transform = self.trans_mat * self.rot_mat
            # transform = global_transform * local_transform

            # idk.setmat4(self.shader, "un_model", transform)
            # idk.drawVertices(idk.getPrimitive(idk.PRIMITIVE_UVSPHERE))

            # Fingertips

            scale        = glm.scale(glm.vec3(0.03))
            joint_matrix = methods.joint_matrix(pos_v, pos_u)
            transform    = self.trans_mat * self.rot_mat * joint_matrix * scale

            idk.setmat4(self.shader, "un_model", transform)
            idk.drawVertices(idk.getPrimitive(idk.PRIMITIVE_UVSPHERE))



    def __draw(self, handLms, whandLms, cam) -> None:

        self.__preprocess_vertices(cam, handLms, whandLms)

        # # Visualise hand orientation 
        # # --------------------------------------------------------------------------------------
        # pos_0   = glm.vec3(translation + self.wlms[0])
        # pos_5   = glm.vec3(translation + self.wlms[5])
        # pos_17  = glm.vec3(translation + self.wlms[17])
        # self.palm_dir = glm.normalize(glm.cross(pos_5 - pos_0, pos_17 - pos_0))
    
        # pos_trans = glm.translate(pos_0)
        # pos_rot   = glm.inverse(glm.lookAt(pos_0, pos_0+self.palm_dir, glm.vec3(0.0, 1.0, 0.0)))
        # pos_scale = glm.scale(glm.vec3(0.03, 0.03, 2))
        # transform = pos_trans * pos_rot * pos_scale

        # idk.setvec3(self.hand_shader, "un_color", glm.vec3(0.0, 0.0, 1.0))
        # idk.setmat4(self.hand_shader, "un_model", transform)
        # idk.drawVertices(idk.getPrimitive(idk.PRIMITIVE_CYLINDER))
        # # --------------------------------------------------------------------------------------


        # # Visualise finger direction 
        # # --------------------------------------------------------------------------------------
        # pos_5 = glm.vec3(translation + self.wlms[5])
        # pos_8 = glm.vec3(translation + self.wlms[8])
        # finger_dir = glm.normalize(pos_8 - pos_5)

        # pos_trans = glm.translate(pos_8)
        # pos_rot   = glm.inverse(glm.lookAt(pos_8, pos_8+finger_dir, glm.vec3(0.0, 1.0, 0.0)))
        # pos_scale = glm.scale(glm.vec3(0.03, 0.03, 2))
        # transform = pos_trans * pos_rot * pos_scale

        # idk.setvec3(self.hand_shader, "un_color", glm.vec3(1.0, 0.0, 0.0))
        # idk.setmat4(self.hand_shader, "un_model", transform)
        # idk.drawVertices(idk.getPrimitive(idk.PRIMITIVE_CYLINDER))
        # # --------------------------------------------------------------------------------------


        for joint_list in JOINT_LISTS:
            self.__draw_joint_list(joint_list, cam)



    def draw(self, handDetector, cam: idk.Camera, handedness: str) -> None:

        results = handDetector.m_results
        if not results or not results.multi_hand_landmarks:
            self.wlms_prev = np.copy(self.wlms)
            self.center_raw_prev = self.center_raw
            return

        handedness_idx = -1
        idx = 0

        for i in results.multi_handedness:
            label = MessageToDict(i)['classification'][0]['label']
            if label == handedness:
                handedness_idx = idx
                break
            idx += 1

        if handedness_idx == -1:
            return # Can't determine handedness

        self.__ready = True

        glUseProgram(self.shader)
        idk.setmat4(self.shader, "un_proj", cam.projection())
        idk.setmat4(self.shader, "un_view", cam.viewMatrix())


        handLms = results.multi_hand_landmarks[handedness_idx]
        whandLms = results.multi_hand_world_landmarks[handedness_idx]

        self.__draw(handLms, whandLms, cam)
        # self.__draw(handLms, whandLms, cam, glm.vec3(6.0,  0.0, -2.0))
        # self.__draw(handLms, whandLms, cam, glm.vec3(6.0, -1.5, -2.0))
