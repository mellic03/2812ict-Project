from sdl2 import *
from sdl2.sdlimage import *
import sdl2.ext
import ctypes
from OpenGL.GL import *
from OpenGL.GL import shaders
import numpy as np
import glm as glm


class Transform:
    def __init__(self) -> None:
        self.__front = glm.vec3(0.0, 0.0, -1.0)
        self.__model_mat = glm.mat4(1.0)

    def translate(self, v: glm.vec3) -> None:
        self.__model_mat = glm.translate(v) * self.__model_mat

    def modelMatrix(self) -> glm.mat4:
        return self.__model_mat


class Camera:

    coupled = True

    def __init__(self, fov, aspect, near, far) -> None:
        self.__fov    = fov
        self.__aspect = aspect
        self.__near   = near
        self.__far    = far

        self.__default_front = glm.vec3( 0.0,  0.0, -1.0 )
        self.__default_right = glm.vec3( 1.0,  0.0,  0.0 )
        self.__default_up    = glm.vec3( 0.0,  1.0,  0.0 )

        self.__pos   = glm.vec3(0.0)
        self.__front = glm.vec3(0.0, 0.0, -1.0)
        self.__right = glm.vec3( 1.0,  0.0,  0.0 )
        self.__up    = glm.vec3( 0.0,  1.0,  0.0 )

        self.__view = glm.lookAt(
            self.__pos,
            self.__pos + self.__front,
            self.__up
        )

        self.__projection = glm.perspective(
            self.__fov,
            self.__aspect,
            self.__near,
            self.__far
        )

        self.__transform = Transform()


    def translate(self, v: glm.vec3) -> None:
        _v = glm.inverse(glm.mat3(self.__view)) * v
        self.__transform.translate(_v)


    def yaw(self, f) -> None:
        self.__view = glm.rotate(self.__view, f, glm.vec3(0.0, 1.0, 0.0))
        self.__right = glm.inverse(self.__view) * self.__default_right
        self.__front = glm.inverse(self.__view) * self.__default_front


    def pitch(self, f) -> None:
        self.__view  = glm.rotate(self.__view, f, self.__right)
        self.__front = glm.inverse(self.__view) * self.__default_front
        self.__up    = glm.inverse(self.__view) * self.__default_up


    def viewMatrix(self) -> glm.mat4:
        return self.__view * glm.inverse(self.__transform.modelMatrix())


    def projection(self) -> glm.mat4:
        return self.__projection


    def front(self) -> glm.vec3:
        return self.__front


    def position(self) -> glm.vec3:
        return glm.vec3(self.__transform.modelMatrix()[3])



