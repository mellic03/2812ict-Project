
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
            float(config["visual"]["skin_r"]) / 255.0,
            float(config["visual"]["skin_g"]) / 255.0,
            float(config["visual"]["skin_b"]) / 255.0
        )
        self.iris_color = glm.vec3(
            float(config["visual"]["iris_r"]) / 255.0,
            float(config["visual"]["iris_g"]) / 255.0,
            float(config["visual"]["iris_b"]) / 255.0
        )
        self.specular = glm.vec3(
            float(config["visual"]["spec_r"]) / 255.0,
            float(config["visual"]["spec_g"]) / 255.0,
            float(config["visual"]["spec_b"]) / 255.0
        )
        self.spec_exp = float(config["visual"]["spec_exp"])

        if config.has_option("visual", "texture_path"):
            self.use_face_texture = True
            texture_path = config["visual"]["texture_path"]
            if texture_path != "":
                texture_path = texture_path.encode('utf-8')
                self.face_mh.glTextureID = idk.loadTexture(texture_path)
        else:
            self.use_face_texture = False

        self.lerp_alpha = float(config["tweaks"]["lerp_alpha"])


    def __reload_shaders(self) -> None:
        self.iris_shader = idk.compileShaderProgram("src/shaders/", "general.vs", "face/iris.fs")
        self.face_shader_tex = idk.compileShaderProgram("src/shaders/", "general.vs", "face/face-tex.fs")
        self.face_shader = idk.compileShaderProgram("src/shaders/", "general.vs", "face/face.fs")


    def __init__(self, configpath: str) -> None:
        self.config_path = configpath

        self.vertices, self.indices = geom.load_CFM("data/vertices.txt", "data/indices.txt")
        self.vbackbuffer = np.empty_like(self.vertices, dtype=np.float32)
        self.face_mh = idk.loadVerticesIndexed(self.vertices, self.indices, GL_DYNAMIC_DRAW)

        self.iris_verts = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], dtype=np.float32)
        self.iris_mh = idk.loadVertices(self.iris_verts, GL_DYNAMIC_DRAW)

        sphere = idk.Model()
        self.sphere_mh = sphere.loadOBJ(b"models/icosphere.obj")

        self.__reload_shaders()
        self.__reload_ini()

        self.ready = False
        self.theta = 0.0


    def __preprocess_vertices(self, facelms) -> None:
        img_w = 640
        img_h = 480

        geom.lmarks_to_np(
            landmarks = facelms.landmark,
            nparray   = self.vbackbuffer,
            aspect    = img_w/img_h
        )

        geom.lerp_verts(self.vertices, self.vbackbuffer, self.lerp_alpha)
        geom.calculate_normals(self.vertices, self.indices)


    def __draw_iris(self, facelms, cam: idk.Camera) -> None:

        aspect = 640/480

        vertices = [  ] # np.ndarray((3, 8), dtype=np.float32)

        v0 = facelms.landmark[FACEMESH_LEFT_IRIS[0][0]]
        v1 = facelms.landmark[FACEMESH_LEFT_IRIS[1][0]]
        v2 = facelms.landmark[FACEMESH_LEFT_IRIS[2][0]]
        v3 = facelms.landmark[FACEMESH_LEFT_IRIS[3][0]]

        vertices += [ aspect*(v0.x-0.5), v0.y-0.5, v0.z, 0, 0, 0, 0, 0 ]
        vertices += [ aspect*(v1.x-0.5), v1.y-0.5, v1.z, 0, 0, 0, 0, 0 ]
        vertices += [ aspect*(v2.x-0.5), v2.y-0.5, v2.z, 0, 0, 0, 0, 0 ]

        # idk.subData(self.iris_mh, vertices)

        vertices = np.array(vertices, dtype=np.float32)

        eee = idk.loadVertices(vertices, GL_DYNAMIC_DRAW)

        rotation = glm.rotate(self.theta, glm.vec3(0.0, 1.0, 0.0))
        translation = glm.translate(glm.vec3(-2.0, -1.5, 0.0))
        scale = glm.scale(glm.vec3(2.0))
        transform =  translation * scale * rotation

        glUseProgram(self.iris_shader)
        idk.setmat4(self.iris_shader, "un_proj", cam.projection())
        idk.setmat4(self.iris_shader, "un_view", cam.viewMatrix())
        idk.setmat4(self.iris_shader, "un_model", transform * glm.scale(glm.vec3(-1, 1, 1)))
        idk.setvec3(self.iris_shader, "un_color", glm.vec3(1.0, 0.0, 1.0))
        idk.drawVertices(eee)


    def __draw_face(self, cam: idk.Camera) -> None:
        current_shader = self.face_shader

        if self.use_face_texture:
            current_shader = self.face_shader_tex

        rotation = glm.rotate(self.theta, glm.vec3(0.0, 1.0, 0.0))
        translation = glm.translate(glm.vec3(-2.0, -1.5, 0.0))
        scale = glm.scale(glm.vec3(2.0))
        transform =  translation * scale * rotation

        glUseProgram(current_shader)
        idk.setmat4(current_shader, "un_view",     cam.viewMatrix())
        idk.setvec3(current_shader, "un_view_pos", cam.position()  )
        idk.setmat4(current_shader, "un_proj",     cam.projection())
        idk.setmat4(current_shader, "un_model",    transform * glm.scale(glm.vec3(-1, 1, 1)))
        idk.setvec3(current_shader, "un_color",    self.skin_color)
        idk.setvec3(current_shader, "un_specular", self.specular)
        idk.setfloat(current_shader, "un_spec_exponent", self.spec_exp)

        glUseProgram(current_shader)
        idk.indexedSubData(self.face_mh.VAO, self.face_mh.VBO, self.vertices)

        if self.use_face_texture:
            idk.drawVerticesIndexedTextured(self.face_mh, self.face_shader_tex)
        else:
            idk.drawVerticesIndexed(self.face_mh)


    def draw(self, faceDetector, cam: idk.Camera, dtime) -> None:

        results = faceDetector.m_results
        if not results or not results.multi_face_landmarks:
            return

        self.ready = True

        for facelms in results.multi_face_landmarks:
            self.__preprocess_vertices(facelms)

        self.__draw_face(cam)

        for facelms in results.multi_face_landmarks:
            self.__draw_iris(facelms, cam)



    def onEvent(self, state, dtime=1.0) -> None:
        if state[SDL_SCANCODE_F5]:
            self.__reload_ini()
            self.__reload_shaders()

