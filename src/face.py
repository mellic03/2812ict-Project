
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


class FaceRenderer:

    def __reload_ini(self) -> None:
        config = configparser.ConfigParser()
        config.read(self.config_path)

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
        self.specular = glm.vec3(
            float(config["color"]["spec_r"]) / 255.0,
            float(config["color"]["spec_g"]) / 255.0,
            float(config["color"]["spec_b"]) / 255.0
        )

        if config.has_option("general", "texture_path"):
            texture_path = config["general"]["texture_path"]
            if texture_path != "":
                texture_path = texture_path.encode('utf-8')
                self.face_mh.glTextureID = idk.loadTexture(texture_path)



    def __init__(self, configpath: str) -> None:
        self.config_path = configpath

        self.face_shader = idk.compileShaderProgram("src/shaders/", "indexed.vs", "indexed.fs")
        self.iris_shader = idk.compileShaderProgram("src/shaders/", "basic.vs", "basic2.fs")
        self.vertices, self.indices = geom.load_CFM("data/vertices.txt", "data/indices.txt")
        self.face_mh = idk.loadVerticesIndexed(self.vertices, self.indices, GL_STATIC_DRAW)

        sphere = idk.Model()
        self.sphere_mh = sphere.loadOBJ(b"models/icosphere.obj", b"textures/face.png")

        self.__reload_ini()
        self.theta = 0.0



    def __draw(self, faceDetector, facelms, cam, ren: idk.Renderer) -> None:
        # self.theta += 0.005
        
        img_w = 640
        img_h = 480
        aspect = img_w / img_h

        for i in range(0, len(facelms.landmark)):
            if 8*i >= self.vertices.size:
                break

            v0 = facelms.landmark[i]
            self.vertices[8*i + 0] = aspect*(v0.x-0.5)
            self.vertices[8*i + 1] = (v0.y-0.5)
            self.vertices[8*i + 2] = v0.z


        geom.calculate_normals(self.vertices, self.indices)
        glBindVertexArray(self.face_mh.VAO)
        glBindBuffer(GL_ARRAY_BUFFER, self.face_mh.VBO)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STREAM_DRAW)    


        # avg = glm.vec3(0.0)

        # for idxpair in FACEMESH_LEFT_IRIS:
        #     idx = idxpair[0]
        #     avg += glm.vec3(
        #         aspect*(facelms.landmark[idx].x - 0.5),
        #         facelms.landmark[idx].y - 0.5,
        #         facelms.landmark[idx].z
        #     )
        # avg /= len(FACEMESH_LEFT_IRIS)

        # transform = glm.translate(glm.vec3(-2.0, -1.5, 0.0)+avg)* glm.scale(glm.vec3(0.1)) * glm.rotate(self.theta, glm.vec3(0.0, 1.0, 0.0))

        # glUseProgram(self.iris_shader)
        # ren.setmat4(self.iris_shader, "un_model", transform)
        # idk.drawVertices(self.sphere_mh)


        transform = glm.translate(
            glm.vec3(-2.0, -1.5, 0.0)) * glm.scale(glm.vec3(2.0)) * glm.rotate(self.theta, glm.vec3(0.0, 1.0, 0.0)
        )

        glUseProgram(self.face_shader)
        ren.setvec3(self.face_shader, "un_color", self.skin_color)
        ren.setvec3(self.face_shader, "un_specular", self.specular)
        ren.setmat4(self.face_shader, "un_model", transform)
        idk.drawVerticesIndexedTextured(self.face_mh, self.face_shader)



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



    def onEvent(self, sdl_keystate) -> None:

        if sdl_keystate[SDL_SCANCODE_F5]:
            self.__reload_ini()
