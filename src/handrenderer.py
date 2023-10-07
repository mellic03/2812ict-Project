
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



def is_grabbing( screen_lms ) -> bool:

    lms = screen_lms.landmark

    x4  = math.fabs(lms[ 4].x)
    x5  = math.fabs(lms[ 5].x)
    x17 = math.fabs(lms[17].x)

    xmax = max(x5, x17)
    xmin = min(x5, x17)

    y0  = math.fabs(lms[ 0].y)
    y5  = math.fabs(lms[ 5].y)
    y8  = math.fabs(lms[ 8].y)
    y9  = math.fabs(lms[ 9].y)
    y12 = math.fabs(lms[12].y)
    y13 = math.fabs(lms[13].y)
    y16 = math.fabs(lms[16].y)
    y17 = math.fabs(lms[17].y)
    y20 = math.fabs(lms[20].y)

    c0 = y0 > y8  > y5
    c1 = y0 > y12 > y9
    c2 = y0 > y16 > y13
    c3 = y0 > y20 > y17
    c4 = xmin < x4 < xmax

    return c0 and c1 and c2 and c3 and c4



class HandRenderer:

    def __reload_ini(self, configpath) -> None:
        config = configparser.ConfigParser()
        config.read(configpath)


        self.measurements = {
            "dist_0_5":     float(config["measurements"]["0-5-dist-mm"]),
            "dist_0_17":    float(config["measurements"]["0-17-dist-mm"]),
            "dist_5_17":    float(config["measurements"]["5-17-dist-mm"])
        }

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

        self.__reload_ini(configpath)

        self.hand_shader = idk.compileShaderProgram("src/shaders/", "general.vs", "hands/hands.fs")

        self.__ready = False

        self.lms = np.zeros((21, 3), dtype=np.float32)
        self.wlms = np.zeros((21, 3), dtype=np.float32)
    
        self.center = [0, 0, 0]
        self.grabbing = False
        self.delta_pos = glm.vec3(0.0)
        self.last_pos  = glm.vec3(0.0)
        self.velocity  = glm.vec3(0.0)
        self.palm_dir  = glm.vec3(0.0, 0.0, 1.0)

        self.rot_mat   = glm.mat4(1.0)
        self.trans_mat = glm.mat4(1.0)
        self.__depth   = 0.0


    
    def setRotation(self, rot: glm.mat4 ) -> None:
        self.rot_mat = rot


    def setTranslation(self, trans: glm.mat4 ) -> None:
        self.trans_mat = trans


    def setDepth(self, depth) -> None:
        self.__depth = depth


    def calculateDepth(self) -> float:

        if self.__ready == False:
            return 1

        p00 = glm.vec2(self.lms[0][0:3])
        p05 = glm.vec2(self.lms[5][0:3])
        p17 = glm.vec2(self.lms[17][0:3])

        f = defs.FOCAL_LENGTH
        W = defs.IMG_W
        H = defs.IMG_H

        depth0 = methods.estimate_depth_mm(f, p00, p05, self.measurements["dist_0_5"],  W, H)
        depth1 = methods.estimate_depth_mm(f, p00, p17, self.measurements["dist_0_17"], W, H)
        depth2 = methods.estimate_depth_mm(f, p05, p17, self.measurements["dist_5_17"], W, H)
        # print("HAND  %.2f,  %.2f,  %.2f" % (depth0, depth1, depth2))

        depth_mm = min([depth0, depth1, depth2])
        depth_m  = depth_mm / 1000.0

        return depth_m


    def is_grabbing(self, whandLms) -> bool:

        wlms = whandLms.landmark

        x4  = math.fabs(wlms[ 4].x) * defs.IMG_W
        x5  = math.fabs(wlms[ 5].x) * defs.IMG_W
        x17 = math.fabs(wlms[17].x) * defs.IMG_W

        xmax = max(x5, x17)
        xmin = min(x5, x17)

        y0  = math.fabs(wlms[ 0].y) * defs.IMG_H
        y5  = math.fabs(wlms[ 5].y) * defs.IMG_H
        y8  = math.fabs(wlms[ 8].y) * defs.IMG_H
        y9  = math.fabs(wlms[ 9].y) * defs.IMG_H
        y12 = math.fabs(wlms[12].y) * defs.IMG_H
        y13 = math.fabs(wlms[13].y) * defs.IMG_H
        y16 = math.fabs(wlms[16].y) * defs.IMG_H
        y17 = math.fabs(wlms[17].y) * defs.IMG_H
        y20 = math.fabs(wlms[20].y) * defs.IMG_H

        # print("%.2f %.2f" % (y5, y17))

        c0 = y0 > y8  > y5
        c1 = y0 > y12 > y9
        c2 = y0 > y16 > y13
        c3 = y0 > y20 > y17
        c4 = xmin < x4 < xmax

        return c0 and c1 and c2 and c3 # and c4


    # Convert landmarks to numpy array and add wrist position to all other landmarks
    def __preprocess_vertices(self, handLms, whandLms) -> None:

        self.lms  = geom.lmarks_to_np(handLms.landmark, self.lms, 1)
        self.wlms = geom.lmarks_to_np(whandLms.landmark, self.wlms, 1, glm.vec2(0.0))


        XYSCALE = 3.0

        self.center = glm.vec3(
            glm.lerp(XYSCALE * self.lms[0][0], self.center[0], 0.8),
            glm.lerp(XYSCALE * self.lms[0][1], self.center[1], 0.8),
            glm.lerp(self.__depth, self.center[2], 0.8)
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

            pos_scale = glm.scale(glm.vec3(0.03, 0.03, 2*dist))
            pos_rot   = glm.inverse(glm.lookAt(pos_u, pos_v, glm.vec3(0.0, 1.0, 0.0)))
            pos_trans = glm.translate(pos_u)
            local_transform = pos_trans * pos_rot * pos_scale
            global_transform = self.trans_mat * self.rot_mat
            transform = global_transform * local_transform


            color = glm.lerp(self.base_color, self.tip_color, i/2)
            if self.grabbing:
                color = glm.lerp(self.grab_base_color, self.grab_tip_color, i/2)
            idk.setvec3(self.hand_shader, "un_color", color)

            # Digits
            idk.setmat4(self.hand_shader, "un_model", transform)
            idk.drawVertices(idk.getPrimitive(idk.PRIMITIVE_CYLINDER))

            # Knuckles
            pos_scale = glm.scale(glm.vec3(0.03))
            pos_trans = glm.translate(pos_u)
            local_transform = pos_trans * pos_rot * pos_scale
            global_transform = self.trans_mat * self.rot_mat
            transform = global_transform * local_transform

            idk.setmat4(self.hand_shader, "un_model", transform)
            idk.drawVertices(idk.getPrimitive(idk.PRIMITIVE_UVSPHERE))

            # Fingertips
            pos_scale = glm.translate(glm.vec3(0.0, 0.0, -dist)) * glm.scale(glm.vec3(0.03))
            pos_trans = glm.translate(pos_v)
            local_transform = pos_trans * pos_rot * pos_scale
            global_transform = self.trans_mat * self.rot_mat
            transform = global_transform * local_transform

            idk.setmat4(self.hand_shader, "un_model", transform)
            idk.drawVertices(idk.getPrimitive(idk.PRIMITIVE_UVSPHERE))



    def __draw(self, handLms, whandLms, cam) -> None:

        self.__preprocess_vertices(handLms, whandLms)

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
            return

        handedness_idx = -1
        idx = 0

        for i in results.multi_handedness:
            label = MessageToDict(i)['classification'][0]['label']
            if label == handedness:
                handedness_idx = idx
                break
            handedness_idx = -1
            idx += 1

        if handedness_idx == -1:
            return # Can't determine handedness

        glUseProgram(self.hand_shader)
        idk.setmat4(self.hand_shader, "un_proj", cam.projection())
        idk.setmat4(self.hand_shader, "un_view", cam.viewMatrix())


        results = handDetector.m_results

        if results and results.multi_hand_landmarks:
            self.__ready = True
            
            handLms = results.multi_hand_landmarks[handedness_idx]
            whandLms = results.multi_hand_world_landmarks[handedness_idx]

            self.__draw(handLms, whandLms, cam)
            # self.__draw(handLms, whandLms, cam, glm.vec3(6.0,  0.0, -2.0))
            # self.__draw(handLms, whandLms, cam, glm.vec3(6.0, -1.5, -2.0))


        self.grabbing = self.is_grabbing(whandLms)

        self.velocity = glm.clamp(0.9*self.velocity, -0.1, +0.1)

        if self.grabbing:
            self.velocity.x += 0.25*self.delta_pos.x
            self.velocity.y += 0.25*self.delta_pos.y
            self.velocity.z += self.delta_pos.z

        cam.translate(-self.velocity)

