from sdl2 import *
from sdl2.sdlimage import *
import sdl2.ext
import ctypes
from OpenGL.GL import *
from OpenGL.GL import shaders
import glm
import numpy as np


class Transform:
    def __init__(self) -> None:
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

        self.__default_front = glm.vec3(0.0, 0.0, 1.0)
        self.__default_right = glm.vec3(1.0, 0.0, 0.0)
        self.__default_up    = glm.vec3(0.0, 1.0, 0.0)

        self.__pos   = glm.vec3(0.0)
        self.__front = glm.vec3(0.0, 0.0, 1.0)
        self.__right = glm.vec3(1.0, 0.0, 0.0)
        self.__up    = glm.vec3(0.0, 1.0, 0.0)

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
        self.__anchor = glm.vec3(0.0)


    def translate(self, v: glm.vec3, scale=glm.vec3(1.0)) -> None:
        _v = glm.inverse(glm.mat3(self.__view)) * v
        _v.x *= scale.x
        _v.y *= scale.y
        _v.z *= scale.z
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
        return self.__view * self.__transform.modelMatrix() * glm.inverse(glm.translate(self.__anchor))


    def setProjection(self, fov, width, height) -> None:
        self.__projection = glm.perspective(
            fov,
            width/height,
            self.__near,
            self.__far
        )

    def anchor(self, pos: glm.vec3) -> None:
        self.__anchor = pos

    def projection(self) -> glm.mat4:
        return self.__projection

    def fov(self) -> float:
        return self.__fov

    def front(self) -> glm.vec3:
        return self.__front


    def position(self) -> glm.vec3:
        return glm.vec3(glm.inverse(self.__transform.modelMatrix())[3])


    def onEvent(self, state, dtime=1.0):
        SPEED = 3.0 * dtime
        TURN  = 3.0 * dtime

        if state[SDL_SCANCODE_D]:
            self.translate(SPEED * glm.vec3( 1.0, 0.0,  0.0))
        if state[SDL_SCANCODE_A]:
            self.translate(SPEED * glm.vec3(-1.0, 0.0,  0.0))
        if state[SDL_SCANCODE_W]:
            self.translate(SPEED * glm.vec3(0.0,  0.0,  1.0), glm.vec3(1, 0, 1))
        if state[SDL_SCANCODE_S]:
            self.translate(SPEED * glm.vec3(0.0,  0.0, -1.0), glm.vec3(1, 0, 1))


        if state[SDL_SCANCODE_Q]:
            self.yaw( TURN)
        if state[SDL_SCANCODE_E]:
            self.yaw(-TURN)

        if state[SDL_SCANCODE_R]:
            self.pitch( TURN)
        if state[SDL_SCANCODE_F]:
            self.pitch(-TURN)

        if state[SDL_SCANCODE_SPACE]:
            self.translate(SPEED * glm.vec3(0.0,  1.0,  0.0))
        if state[SDL_SCANCODE_LCTRL]:
            self.translate(SPEED * glm.vec3(0.0, -1.0,  0.0))

