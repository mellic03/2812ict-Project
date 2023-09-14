
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
        self.face_mh = idk.loadVerticesIndexed(self.vertices, self.indices, GL_DYNAMIC_DRAW)

        sphere = idk.Model()
        self.sphere_mh = sphere.loadOBJ(b"models/icosphere.obj")

        self.__reload_shaders()
        self.__reload_ini()

        self.theta = 0.0


    def __draw(self, facelms, dtime) -> None:
        # self.theta += 0.005
        
        img_w = 640
        img_h = 480

        new_verts = np.zeros(self.vertices.shape, dtype=np.float32)

        geom.lmarks_to_np(
            landmarks = facelms.landmark,
            nparray   = new_verts,
            aspect    = img_w/img_h
        )

        geom.lerp_verts(self.vertices, new_verts, self.lerp_alpha)
        geom.calculate_normals(self.vertices, self.indices)
        self.draw_verts(self.vertices)



    def draw(self, faceDetector, cam: idk.Camera, dtime) -> None:
        results = faceDetector.m_results
        if not results or not results.multi_face_landmarks:
            return
      
        glUseProgram(self.iris_shader)
        idk.setmat4(self.iris_shader, "un_view", cam.viewMatrix())
        idk.setmat4(self.iris_shader, "un_proj", cam.projection())


        current_shader = self.face_shader
        if self.use_face_texture:
            current_shader = self.face_shader_tex

        glUseProgram(current_shader)
        idk.setmat4(current_shader, "un_view",      cam.viewMatrix())
        idk.setvec3(current_shader, "un_view_pos",  cam.position()  )
        idk.setmat4(current_shader, "un_proj",      cam.projection())


        rotation = glm.rotate(self.theta, glm.vec3(0.0, 1.0, 0.0))
        translation = glm.translate(glm.vec3(-2.0, -1.5, 0.0))
        scale = glm.scale(glm.vec3(2.0))
        transform =  translation * scale * rotation

        idk.setmat4(current_shader, "un_model",    transform)
        idk.setvec3(current_shader, "un_color",    self.skin_color)
        idk.setvec3(current_shader, "un_specular", self.specular)
        idk.setfloat(current_shader, "un_spec_exponent", self.spec_exp)


        results = faceDetector.m_results
        if results and results.multi_face_landmarks:
            for facelms in results.multi_face_landmarks:
                self.__draw(facelms, dtime)


    def draw_verts(self, vertices) -> None:
        idk.indexedSubData(self.face_mh.VAO, self.face_mh.VBO, vertices)
        if self.use_face_texture:
            idk.drawVerticesIndexedTextured(self.face_mh, self.face_shader_tex)
        else:
            idk.drawVerticesIndexed(self.face_mh)


    def onEvent(self, state, dtime=1.0) -> None:
        if state[SDL_SCANCODE_F5]:
            self.__reload_ini()
            self.__reload_shaders()
