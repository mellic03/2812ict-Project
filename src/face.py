
from OpenGL.GL import *
import glm as glm

import idk

import numpy as np
import cv2 as cv
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import math

import configparser
import geometrymethods as geom

from face_vertices import *


class FaceRenderer:

    def __init__(self, configpath: str) -> None:
        config = configparser.ConfigParser()
        config.read(configpath)

        self.skin_color = glm.vec3(
            float(config["color"]["skin_r"]) / 255.0,
            float(config["color"]["skin_g"]) / 255.0,
            float(config["color"]["skin_b"]) / 255.0
        )
        self.iris_color = glm.vec3(
            float(config["color"]["iris_r"]) / 255.0,
            float(config["color"]["iris_g"]) / 255.0,
            float(config["color"]["iris_b"]) / 255.0
        )


        self.face_shader = idk.compileShaderProgram("src/shaders/", "basic.vs", "basic.fs")
        self.iris_shader = idk.compileShaderProgram("src/shaders/", "basic.vs", "basic2.fs")

        uvsphere = idk.Model()
        unit = idk.Model()
        facemodel = idk.Model()

        self.uvsphere_h = uvsphere.loadOBJ(b"models/cube/", b"icosphere.obj", b"cube.mtl", b"container.png")
        self.unit_h = unit.loadOBJ(b"models/cube/", b"icosphere.obj", b"cube.mtl", b"container.png")
        self.facemodel_h = facemodel.loadOBJ(
            b"models/cube/", b"icosphere.obj",
            b"cube.mtl", b"container.png",
            GL_STREAM_DRAW
        )        
        self.theta = 0.0


    def __draw(self, faceDetector, facelms, cam, ren: idk.Renderer) -> None:
        # self.theta += 0.005

        img_w = 640
        img_h = 480
        aspect = img_w / img_h

        vertices = []

        for i in range(0, len(FACEMESH_TESSELATION)):
            idx = FACEMESH_TESSELATION[i][0]
            v0 = facelms.landmark[idx]
            vertices += [aspect*(v0.x-0.5), (v0.y-0.5), v0.z]
            vertices += [ 0.0,  1.0, 0.0 ]
            vertices += [ 0.0,  0.0 ]

        npverts = np.array(vertices, dtype=np.float32)
        geom.process_vertices(npverts)



        # NPVERTS = np.array(vertices, dtype=np.float32)
        glBindVertexArray(self.facemodel_h.VAO)
        glBindBuffer(GL_ARRAY_BUFFER, self.facemodel_h.VBO)
        glBufferData(GL_ARRAY_BUFFER, npverts.nbytes, npverts, GL_STREAM_DRAW)    

        glUseProgram(self.face_shader)
        ren.setvec3(self.face_shader, "un_color", self.skin_color)
        ren.setmat4(self.face_shader, "un_model", glm.translate(
            glm.vec3(-2.0, -1.5, 0.0))
            * glm.scale(glm.vec3(2.0))
            * glm.rotate(self.theta, glm.vec3(0.0, 1.0, 0.0))
        )
        idk.drawVertices(self.facemodel_h)


        vertices = []
        for i in range(0, len(FACEMESH_LEFT_IRIS), 4):
            idx0 = FACEMESH_LEFT_IRIS[i][0]
            idx1 = FACEMESH_LEFT_IRIS[i+1][0]
            idx2 = FACEMESH_LEFT_IRIS[i+2][0]
            idx3 = FACEMESH_LEFT_IRIS[i+3][0]

            v0 = facelms.landmark[idx0]
            v1 = facelms.landmark[idx1]
            v2 = facelms.landmark[idx2]
            v3 = facelms.landmark[idx3]

            vertices += [aspect*(v0.x-0.5), (v0.y-0.5), v0.z]
            vertices += [ 0.0,  1.0, 0.0 ]
            vertices += [ 0.0,  0.0 ]

            vertices += [aspect*(v1.x-0.5), (v1.y-0.5), v1.z]
            vertices += [ 0.0,  1.0, 0.0 ]
            vertices += [ 0.0,  0.0 ]

            vertices += [aspect*(v2.x-0.5), (v2.y-0.5), v2.z]
            vertices += [ 0.0,  1.0, 0.0 ]
            vertices += [ 0.0,  0.0 ]

            vertices += [aspect*(v2.x-0.5), (v2.y-0.5), v2.z]
            vertices += [ 0.0,  1.0, 0.0 ]
            vertices += [ 0.0,  0.0 ]

            vertices += [aspect*(v3.x-0.5), (v3.y-0.5), v3.z]
            vertices += [ 0.0,  1.0, 0.0 ]
            vertices += [ 0.0,  0.0 ]

            vertices += [aspect*(v0.x-0.5), (v0.y-0.5), v0.z]
            vertices += [ 0.0,  1.0, 0.0 ]
            vertices += [ 0.0,  0.0 ]


        for i in range(0, len(FACEMESH_RIGHT_IRIS), 4):
            idx0 = FACEMESH_RIGHT_IRIS[i][0]
            idx1 = FACEMESH_RIGHT_IRIS[i+1][0]
            idx2 = FACEMESH_RIGHT_IRIS[i+2][0]
            idx3 = FACEMESH_RIGHT_IRIS[i+3][0]

            v0 = facelms.landmark[idx0]
            v1 = facelms.landmark[idx1]
            v2 = facelms.landmark[idx2]
            v3 = facelms.landmark[idx3]

            vertices += [aspect*(v0.x-0.5), (v0.y-0.5), v0.z]
            vertices += [ 0.0,  1.0, 0.0 ]
            vertices += [ 0.0,  0.0 ]

            vertices += [aspect*(v1.x-0.5), (v1.y-0.5), v1.z]
            vertices += [ 0.0,  1.0, 0.0 ]
            vertices += [ 0.0,  0.0 ]

            vertices += [aspect*(v2.x-0.5), (v2.y-0.5), v2.z]
            vertices += [ 0.0,  1.0, 0.0 ]
            vertices += [ 0.0,  0.0 ]

            vertices += [aspect*(v2.x-0.5), (v2.y-0.5), v2.z]
            vertices += [ 0.0,  1.0, 0.0 ]
            vertices += [ 0.0,  0.0 ]

            vertices += [aspect*(v3.x-0.5), (v3.y-0.5), v3.z]
            vertices += [ 0.0,  1.0, 0.0 ]
            vertices += [ 0.0,  0.0 ]

            vertices += [aspect*(v0.x-0.5), (v0.y-0.5), v0.z]
            vertices += [ 0.0,  1.0, 0.0 ]
            vertices += [ 0.0,  0.0 ]


        NPVERTS2 = np.array(vertices, dtype=np.float32)
        glBindVertexArray(self.facemodel_h.VAO)
        glBindBuffer(GL_ARRAY_BUFFER, self.facemodel_h.VBO)
        glBufferData(GL_ARRAY_BUFFER, NPVERTS2.nbytes, NPVERTS2, GL_STREAM_DRAW)    

        glUseProgram(self.iris_shader)
        ren.setvec3(self.iris_shader, "un_color", self.iris_color)
        ren.setmat4(self.iris_shader, "un_model", glm.translate(
            glm.vec3(-2.0, -1.5, 0.0))
            * glm.scale(glm.vec3(2.0))
            * glm.rotate(self.theta, glm.vec3(0.0, 1.0, 0.0))
        )
        idk.drawVertices(self.facemodel_h)





    def draw(self, faceDetector, cam: idk.Camera, ren: idk.Renderer) -> None:
        glUseProgram(self.iris_shader)
        ren.setmat4(self.iris_shader, "un_view", cam.viewMatrix())
        ren.setmat4(self.iris_shader, "un_proj", cam.projection())

        glUseProgram(self.face_shader)
        ren.setmat4(self.face_shader, "un_view",      cam.viewMatrix())
        ren.setvec3(self.face_shader, "un_view_pos",  cam.position()  )
        ren.setmat4(self.face_shader, "un_proj",      cam.projection())

        results = faceDetector.m_results
        if results and results.multi_face_landmarks:
            for facelms in results.multi_face_landmarks:
                self.__draw(faceDetector, facelms, cam, ren)

