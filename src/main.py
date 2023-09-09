# OpenGL -------------------------------------------
# This program requires a python wrapper for OpenGL
# along with SDL2, numpy and ctypes.
# pip install ctypes numpy pysdl2 PyOpenGL PyOpenGL_accelerate
# --------------------------------------------------
import idk
from OpenGL.GL import *
import glm as glm

from sdl2 import *
from sdl2.sdlimage import *
import sdl2.ext

import threading
import cv2 as cv

import sys
import os

from detectors import *
from hand import HandRenderer
from face import FaceRenderer


ren = idk.Renderer(b"window", 1500, 1200, False )
results = None
img_w = None
img_h = None




def cv_thread_fn( handDetector: HandDetector, faceDetector: FaceDetector ):
    cap = cv.VideoCapture(0)
    cap.set(cv.CAP_PROP_FRAME_WIDTH,  640)
    cap.set(cv.CAP_PROP_FRAME_HEIGHT, 480)

    while ren.running():
        res, img = cap.read()

        faceDetector.detect(img)
        img = faceDetector.draw(img)

        handDetector.detect(img)
        img = handDetector.draw(img)

        cv.imshow("Image", img)
        cv.waitKey(1)



class SDL2_InputHandler:

    def __init__(self) -> None:
        pass

    def events(self, cam: idk.Camera) -> None:
        SPEED = 0.05

        state = sdl2.SDL_GetKeyboardState(None)
        if state[SDL_SCANCODE_D]:
            cam.translate(SPEED * glm.vec3(-1.0, 0.0,  0.0))
        if state[SDL_SCANCODE_A]:
            cam.translate(SPEED * glm.vec3( 1.0, 0.0,  0.0))
        if state[SDL_SCANCODE_W]:
            cam.translate(SPEED * glm.vec3(0.0,  0.0, -1.0))
        if state[SDL_SCANCODE_S]:
            cam.translate(SPEED * glm.vec3(0.0,  0.0,  1.0))

        if state[SDL_SCANCODE_Q]:
            cam.yaw( 0.01)
        if state[SDL_SCANCODE_E]:
            cam.yaw(-0.01)

        if state[SDL_SCANCODE_R]:
            cam.pitch( 0.01)
        if state[SDL_SCANCODE_F]:
            cam.pitch(-0.01)

        if state[SDL_SCANCODE_C]:
            cam.coupled = not cam.coupled
            cam.last_pos = cam.position()



def gl_thread_fn( handDetector: HandDetector, faceDetector: FaceDetector ):

    width = 1500
    height = 1200
    ren.ren_init()
    glDisable(GL_CULL_FACE)

    cam = idk.Camera(80.0, width/height, 0.1, 10000.0)
    cam.translate(glm.vec3(-1.0, -1.0, -1.0))
    cam.yaw(glm.radians(180))
    inputHandler = SDL2_InputHandler()

    room = idk.Model()
    room_h = room.loadOBJ(b"models/cube/", b"plane.obj", b"cube.mtl", b"palette.png")

    tex_shader = idk.compileShaderProgram("src/shaders/", "textured.vs", "textured.fs")
    idx_shader = idk.compileShaderProgram("src/shaders/", "indexed.vs", "basic.fs")

    glUseProgram(tex_shader)
    ren.setmat4(tex_shader, "proj", cam.projection())

    handObj = HandRenderer("config/hand.ini")
    faceObj = FaceRenderer("config/face.ini")


    vertices, indices = loadBuffer()
    face_mh = idk.loadVerticesIndexed(vertices, indices, GL_STATIC_DRAW)


    while (ren.running()):
        ren.beginFrame()

        results = handDetector.m_results
        if results and results.multi_hand_landmarks:
            handObj.draw(handDetector, cam, ren)

        results = faceDetector.m_results
        if results and results.multi_face_landmarks:
            faceObj.draw(faceDetector, cam, ren)

        # glUseProgram(tex_shader)
        # ren.setmat4(tex_shader, "un_view",      cam.viewMatrix())
        # ren.setvec3(tex_shader, "un_view_pos",  cam.position()  )
        # ren.setvec3(tex_shader, "un_color",     glm.vec3(1.0)   )
        # ren.setmat4(tex_shader, "model",        glm.mat4(1.0)   )
        # ren.drawVerticesTextured(tex_shader, room_h)

        glUseProgram(idx_shader)
        ren.setmat4(idx_shader, "un_proj",  cam.projection())
        ren.setmat4(idx_shader, "un_view",  cam.viewMatrix())
        ren.setmat4(idx_shader, "un_model", glm.mat4(1.0))
        ren.setvec3(idx_shader, "un_view_pos",  cam.position())
        ren.setvec3(idx_shader, "un_color",  glm.vec3(0.5, 1.0, 0.7))

        idk.drawVerticesIndexed(face_mh)
        inputHandler.events(cam)

        ren.endFrame()



def loadBuffer():
    vertices = []
    indices  = []
    
    fh = open("data/face_vertex_buffer.txt", "r")
    for line in fh:
        vertices.append(float(line))
    
    fh = open("data/face_index_buffer.txt", "r")
    for line in fh:
        indices.append(int(line))
    
    return vertices, indices


def main():

    handDetector = HandDetector()
    faceDetector = FaceDetector()

    t1 = threading.Thread(target=gl_thread_fn,  args=(handDetector, faceDetector,))
    t2 = threading.Thread(target=cv_thread_fn,  args=(handDetector, faceDetector,))

    t1.start()
    t2.start()

    t1.join()
    t2.join()



if __name__ == "__main__":
    main()

