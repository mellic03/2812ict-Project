
from OpenGL.GL import *
import glm as glm

import idk

import numpy as np
from google.protobuf.json_format import MessageToDict
import math

import configparser
import libgeometry as geom

import definitions as defs


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

        uvsphere = idk.Model()
        unit = idk.Model()
        
        self.uvsphere_h = uvsphere.loadOBJ(b"models/icosphere.obj")
        self.unit_h = unit.loadOBJ(b"models/cylinder.obj")

        self.lms = np.zeros((21, 3), dtype=np.float32)
        self.wlms = np.zeros((21, 3), dtype=np.float32)
    
        self.center = [0, 0, 0]
        self.grabbing = False
        self.delta_pos = glm.vec3(0.0)
        self.last_pos  = glm.vec3(0.0)
        self.velocity  = glm.vec3(0.0)
        self.palm_dir  = glm.vec3(0.0, 0.0, 1.0)


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


    def depth_estimate(self, j1_enum, j2_enum, real):

        res_x = defs.IMG_W
        res_y = defs.IMG_H
        f = defs.FOCAL_LENGTH

        x0 = self.lms[j1_enum][0]
        y0 = self.lms[j1_enum][1]
        
        x1 = self.lms[j2_enum][0]
        y1 = self.lms[j2_enum][1]

        x0p = x0 * res_x
        x1p = x1 * res_x
        y0p = y0 * res_y
        y1p = y1 * res_y

        pixel_dist = np.sqrt((x0p - x1p)**2 + (y0p-y1p)**2)
        depth = (f * real) / pixel_dist

        return depth



    # Convert landmarks to numpy array and add wrist position to all other landmarks
    def __preprocess_vertices(self, handLms, whandLms) -> None:

        self.lms  = geom.lmarks_to_np(handLms.landmark, self.lms, 1)
        self.wlms = geom.lmarks_to_np(whandLms.landmark, self.wlms, 1, glm.vec2(0.0))


        # Depth estimation
        # --------------------------------------------------------------------------------------
        depth0 = self.depth_estimate(WRIST,     INDEX_FINGER_MCP, DIST_0_5)
        depth1 = self.depth_estimate(PINKY_MCP, INDEX_FINGER_MCP, DIST_5_17)
        depth2 = self.depth_estimate(PINKY_MCP, WRIST,            DIST_0_17)
        depth_mm  = min([depth0, depth1, depth2])

        depth_m = depth_mm / 1000.0 # convert to metres
        # --------------------------------------------------------------------------------------

        MIN_DEPTH = -0.1
        MAX_DEPTH = -1.1

        XYSCALE = 3.0

        self.center = glm.vec3(
            glm.lerp(XYSCALE * self.lms[0][0], self.center[0], 0.8),
            glm.lerp(XYSCALE * self.lms[0][1], self.center[1], 0.8),
            glm.lerp(glm.clamp(MAX_DEPTH + depth_m, MAX_DEPTH, MIN_DEPTH), self.center[2], 0.8)
        )

        # Add center position to all other positions
        # --------------------------------------------------------------------------------------
        for i in range(0, len(self.wlms)):
            self.wlms[i][0] += self.center.x
            self.wlms[i][1] += self.center.y
            self.wlms[i][2] += self.center.z
        # --------------------------------------------------------------------------------------



    def __draw_joint_list(self, joint_list, cam: idk.Camera, translation: glm.vec3) -> None:

        for i in range(0, len(joint_list)-1):

            pos_u = translation + glm.vec3(self.wlms[joint_list[i+0]])
            pos_v = translation + glm.vec3(self.wlms[joint_list[i+1]])

            dist = glm.distance(pos_v, pos_u)

            pos_scale = glm.scale(glm.vec3(0.03, 0.03, 2*dist))
            pos_rot   = glm.inverse(glm.lookAt(pos_u, pos_v, glm.vec3(0.0, 1.0, 0.0)))
            pos_trans = glm.translate(pos_u)
            transform = pos_trans * pos_rot * pos_scale

            color = glm.lerp(self.base_color, self.tip_color, i/2)
            if self.grabbing:
                color = glm.lerp(self.grab_base_color, self.grab_tip_color, i/2)
            idk.setvec3(self.hand_shader, "un_color", color)

            # Digits
            idk.setmat4(self.hand_shader, "un_model", transform)
            idk.drawVertices(self.unit_h)

            # Knuckles
            pos_scale = glm.scale(glm.vec3(0.03))
            pos_trans = glm.translate(pos_u)
            transform = pos_trans * pos_rot * pos_scale
            idk.setmat4(self.hand_shader, "un_model", transform)
            idk.drawVertices(self.uvsphere_h)

            # Fingertips
            pos_scale = glm.translate(glm.vec3(0.0, 0.0, -dist)) * glm.scale(glm.vec3(0.03))
            pos_trans = glm.translate(pos_v)
            transform = pos_trans * pos_rot * pos_scale
            idk.setmat4(self.hand_shader, "un_model", transform)
            idk.drawVertices(self.uvsphere_h)



    def __draw(self, handLms, whandLms, cam, translation=glm.vec3(0.0)) -> None:

        self.__preprocess_vertices(handLms, whandLms)

        # Visualise hand orientation 
        # --------------------------------------------------------------------------------------
        pos_0   = glm.vec3(translation + self.wlms[0])
        pos_5   = glm.vec3(translation + self.wlms[5])
        pos_17  = glm.vec3(translation + self.wlms[17])
        self.palm_dir = glm.normalize(glm.cross(pos_5 - pos_0, pos_17 - pos_0))
    
        pos_trans = glm.translate(pos_0)
        pos_rot   = glm.inverse(glm.lookAt(pos_0, pos_0+self.palm_dir, glm.vec3(0.0, 1.0, 0.0)))
        pos_scale = glm.scale(glm.vec3(0.03, 0.03, 2))
        transform = pos_trans * pos_rot * pos_scale

        idk.setvec3(self.hand_shader, "un_color", glm.vec3(0.0, 0.0, 1.0))
        idk.setmat4(self.hand_shader, "un_model", transform)
        idk.drawVertices(self.unit_h)
        # --------------------------------------------------------------------------------------


        # Visualise finger direction 
        # --------------------------------------------------------------------------------------
        pos_5 = glm.vec3(translation + self.wlms[5])
        pos_8 = glm.vec3(translation + self.wlms[8])
        finger_dir = glm.normalize(pos_8 - pos_5)

        pos_trans = glm.translate(pos_8)
        pos_rot   = glm.inverse(glm.lookAt(pos_8, pos_8+finger_dir, glm.vec3(0.0, 1.0, 0.0)))
        pos_scale = glm.scale(glm.vec3(0.03, 0.03, 2))
        transform = pos_trans * pos_rot * pos_scale

        idk.setvec3(self.hand_shader, "un_color", glm.vec3(1.0, 0.0, 0.0))
        idk.setmat4(self.hand_shader, "un_model", transform)
        idk.drawVertices(self.unit_h)
        # --------------------------------------------------------------------------------------


        for joint_list in JOINT_LISTS:
            self.__draw_joint_list(joint_list, cam, translation)



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
            handLms = results.multi_hand_landmarks[handedness_idx]
            whandLms = results.multi_hand_world_landmarks[handedness_idx]
            self.__draw(handLms, whandLms, cam, glm.vec3(0.0,  cam.position().y, 0.0))
            # self.__draw(handLms, whandLms, cam, glm.vec3(6.0,  0.0, -2.0))
            # self.__draw(handLms, whandLms, cam, glm.vec3(6.0, -1.5, -2.0))


        self.grabbing = self.is_grabbing(whandLms)

        self.velocity = glm.clamp(0.9*self.velocity, -0.1, +0.1)

        if self.grabbing:
            self.velocity.x += 0.25*self.delta_pos.x
            self.velocity.y += 0.25*self.delta_pos.y
            self.velocity.z += self.delta_pos.z

        cam.translate(-self.velocity)

