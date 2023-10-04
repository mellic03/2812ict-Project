
from OpenGL.GL import *
import glm as glm

import idk
from sdl2 import *

import numpy as np
import configparser
import libgeometry as geom

from face_vertices import *

import definitions as defs


def collect_avg( vertices ) -> glm.vec3:
    avg = glm.vec3(0.0)
    count = 0
    for i in range(0, len(vertices), 8):
        avg += glm.vec3(
            vertices[i+0],
            vertices[i+1],
            vertices[i+2],
        )
        count += 1
    return avg / count


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
        self.iris_shader = idk.compileShaderProgram(
            "src/shaders/", "general.vs", "face/iris.fs"
        )
        self.face_shader_tex = idk.compileShaderProgram(
            "src/shaders/", "general.vs", self.face_shader_tex_path
        )
        self.face_shader = idk.compileShaderProgram(
            "src/shaders/", "general.vs", self.face_shader_path
        )


    def __init__(self, configpath: str, eyeholes: bool = True) -> None:
        self.config_path = configpath

        self.iris_shader_path = "face/iris.fs"

        if defs.USE_PYTHON:
            self.face_shader_tex_path = "face/face-tex-py.fs"
            self.face_shader_path = "face/face-py.fs"
        else:
            self.face_shader_tex_path = "face/face-tex.fs"
            self.face_shader_path = "face/face.fs"

        filepath = "data/indices.txt"
        if eyeholes:
            filepath = "data/indices2.txt"

        self.vertices, self.indices = geom.load_CFM("data/vertices.txt", filepath)
        self.vbackbuffer = np.empty_like(self.vertices, dtype=np.float32)

        self.__landmarks2D = [glm.vec2(0)] * self.vertices.size
        self.__landmarks3D = []


        self.face_mh = idk.loadVerticesIndexed(self.vertices, self.indices, GL_DYNAMIC_DRAW)

        self.iris_verts = np.array([0]*8*12, dtype=np.float32)
        self.iris_mh = idk.loadVertices(self.iris_verts, GL_DYNAMIC_DRAW)
        self.iris_verts = self.iris_verts.reshape((12, 8))
        self.iris_l_pos = glm.vec3(0.0)
        self.iris_l_nrm = glm.vec3(0.0)
        self.iris_r_pos = glm.vec3(0.0)
        self.iris_r_nrm = glm.vec3(0.0)

        self.__reload_shaders()
        self.__reload_ini()

        self.ready = False
        self.theta = 3.14159


    def __preprocess_vertices(self, facelms) -> None:
        aspect = defs.IMG_W / defs.IMG_H

        self.vbackbuffer = geom.lmarks_to_np(facelms.landmark, self.vbackbuffer, aspect, glm.vec2(-0.5, -0.5))
        self.__landmarks2D = geom.lmarks_to_glm(facelms.landmark, self.__landmarks2D, aspect, glm.vec2(-0.5, -0.5))

        geom.lerp_verts(self.vertices, self.vbackbuffer, self.lerp_alpha)
        geom.calculate_normals(self.vertices, self.indices)


    def landmarks2D(self) -> list[glm.vec2]:
        return self.__landmarks2D


    def __draw_iris(self, facelms, cam: idk.Camera, translation = glm.vec3(0.0)) -> None:
        aspect = defs.IMG_W / defs.IMG_H

        v0 = facelms.landmark[FACEMESH_RIGHT_IRIS[0][0]]
        v1 = facelms.landmark[FACEMESH_RIGHT_IRIS[1][0]]
        v2 = facelms.landmark[FACEMESH_RIGHT_IRIS[2][0]]
        v3 = facelms.landmark[FACEMESH_RIGHT_IRIS[3][0]]

        vertices1 = [  ]
        vertices1 += [ aspect*(v0.x-0.5), v0.y-0.5, v0.z, 0, 0, 0, 0, 0 ]
        vertices1 += [ aspect*(v1.x-0.5), v1.y-0.5, v1.z, 0, 0, 0, 0, 0 ]
        vertices1 += [ aspect*(v2.x-0.5), v2.y-0.5, v2.z, 0, 0, 0, 0, 0 ]
        vertices1 += [ aspect*(v0.x-0.5), v0.y-0.5, v0.z, 0, 0, 0, 0, 0 ]
        vertices1 += [ aspect*(v2.x-0.5), v2.y-0.5, v2.z, 0, 0, 0, 0, 0 ]
        vertices1 += [ aspect*(v3.x-0.5), v3.y-0.5, v3.z, 0, 0, 0, 0, 0 ]
        self.iris_r_pos = collect_avg(vertices1)

        v0 = glm.vec3(v0.x, v0.y, v0.z)
        v1 = glm.vec3(v1.x, v1.y, v1.z)
        v2 = glm.vec3(v2.x, v2.y, v2.z)
        v3 = glm.vec3(v3.x, v3.y, v3.z)
        self.iris_r_nrm = glm.normalize(glm.cross(v2-v0, v3-v0))


        v0 = facelms.landmark[FACEMESH_LEFT_IRIS[0][0]]
        v1 = facelms.landmark[FACEMESH_LEFT_IRIS[1][0]]
        v2 = facelms.landmark[FACEMESH_LEFT_IRIS[2][0]]
        v3 = facelms.landmark[FACEMESH_LEFT_IRIS[3][0]]

        vertices2 = [  ]
        vertices2 += [ aspect*(v0.x-0.5), v0.y-0.5, v0.z, 0, 0, 0, 0, 0 ]
        vertices2 += [ aspect*(v1.x-0.5), v1.y-0.5, v1.z, 0, 0, 0, 0, 0 ]
        vertices2 += [ aspect*(v2.x-0.5), v2.y-0.5, v2.z, 0, 0, 0, 0, 0 ]
        vertices2 += [ aspect*(v0.x-0.5), v0.y-0.5, v0.z, 0, 0, 0, 0, 0 ]
        vertices2 += [ aspect*(v2.x-0.5), v2.y-0.5, v2.z, 0, 0, 0, 0, 0 ]
        vertices2 += [ aspect*(v3.x-0.5), v3.y-0.5, v3.z, 0, 0, 0, 0, 0 ]
        self.iris_l_pos = collect_avg(vertices2)

        v0 = glm.vec3(v0.x, v0.y, v0.z)
        v1 = glm.vec3(v1.x, v1.y, v1.z)
        v2 = glm.vec3(v2.x, v2.y, v2.z)
        v3 = glm.vec3(v3.x, v3.y, v3.z)
        self.iris_l_nrm = glm.normalize(glm.cross(v2-v0, v3-v0))

        vertices = np.array(vertices1+vertices2, dtype=np.float32).reshape((12, 8))
        geom.lerp_verts(self.iris_verts, vertices, self.lerp_alpha)
        idk.subData(self.iris_mh, self.iris_verts)

        rotation = glm.rotate(self.theta, glm.vec3(0.0, 1.0, 0.0))
        trans = glm.translate(translation)
        scale = glm.scale(glm.vec3(2.0))
        transform =  trans * scale * rotation

        glUseProgram(self.iris_shader)
        idk.setmat4(self.iris_shader, "un_proj", cam.projection())
        idk.setmat4(self.iris_shader, "un_view", cam.viewMatrix())
        idk.setmat4(self.iris_shader, "un_model", transform*glm.scale(glm.vec3(-1, 1, 1)))
        idk.setvec3(self.iris_shader, "un_color", self.iris_color)
        idk.drawVertices(self.iris_mh)


    def __draw_face(self, cam: idk.Camera, translation = glm.vec3(0.0)) -> None:
        current_shader = self.face_shader

        if self.use_face_texture:
            current_shader = self.face_shader_tex

        rotation    = glm.rotate(self.theta, glm.vec3(0.0, 1.0, 0.0))
        trans       = glm.translate(translation)
        scale       = glm.scale(glm.vec3(2.0))
        transform   = trans * rotation * scale

        glUseProgram(current_shader)
        idk.setmat4(current_shader,  "un_view",     cam.viewMatrix())
        idk.setmat4(current_shader,  "un_proj",     cam.projection())
        idk.setmat4(current_shader,  "un_model",    transform*glm.scale(glm.vec3(-1, 1, 1)))
        idk.setvec3(current_shader,  "un_color",    self.skin_color)
        idk.setvec3(current_shader,  "un_specular", self.specular)
        idk.setvec3(current_shader,  "un_view_pos", cam.position())
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

        self.__draw_face(cam, glm.vec3(6.0, -1.5, -2.0))
        self.__draw_face(cam, glm.vec3(12.0, -1.5, -2.0))

        for facelms in results.multi_face_landmarks:
            self.__draw_iris(facelms, cam, glm.vec3(6.0, -1.5, -2.0))
            self.__draw_iris(facelms, cam, glm.vec3(12.0, -1.5, -2.0))


    def onEvent(self, state, dtime=1.0) -> None:
        if state[SDL_SCANCODE_F5]:
            self.__reload_ini()
            self.__reload_shaders()

