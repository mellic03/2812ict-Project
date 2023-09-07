# OpenGL -------------------------------------------
# This program requires a python wrapper for OpenGL
# along with SDL2, numpy and ctypes.
# pip install ctypes numpy pysdl2 PyOpenGL PyOpenGL_accelerate
# --------------------------------------------------
import idk
from OpenGL.GL import *
import glm as glm

import configparser

import threading
import numpy as np
import cv2 as cv
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import math

from detectors import *
from hand import CV_MP_Hand

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
        handDetector.detect(img)
        handDetector.draw()



def gl_thread_fn( handDetector: HandDetector, faceDetector: FaceDetector ):

    width = 1500
    height = 1200
    ren.ren_init()
    cam = idk.Camera(80.0, width/height, 0.1, 100.0)
    cam.translate(glm.vec3(0.0, -1.0, 0.0))

    room = idk.Model()
    room_h = room.loadOBJ(b"models/cube/", b"plane.obj", b"cube.mtl", b"palette.png")

    basic_shader: GLuint = ren.compileShaderProgram("src/shaders/", "basic.vs", "basic.fs")
    tex_shader: GLuint = ren.compileShaderProgram("src/shaders/", "textured.vs", "textured.fs")


    handObj = CV_MP_Hand()

    while (ren.running()):
        ren.beginFrame()

        glUseProgram(basic_shader)
        ren.setmat4(basic_shader, "un_view",        cam.viewMatrix())
        ren.setvec3(basic_shader, "un_view_pos",    cam.position()  )
        ren.setmat4(basic_shader, "proj",           cam.projection())

        results = handDetector.m_results
        if results and results.multi_hand_landmarks:
            handObj.draw(handDetector, basic_shader, cam, ren)


        glUseProgram(tex_shader)
        ren.setmat4(tex_shader, "un_view",      cam.viewMatrix())
        ren.setvec3(tex_shader, "un_view_pos",  cam.position()  )
        ren.setvec3(tex_shader, "un_color",     glm.vec3(1.0)   )
        ren.setmat4(tex_shader, "proj",         cam.projection())
        ren.setmat4(tex_shader, "model",        glm.mat4(1.0)   )
        ren.drawVerticesTextured(tex_shader, room_h)

        ren.processKeyEvents(cam)

        ren.endFrame()




def main():

    config = configparser.ConfigParser()
    config.read("config.ini")
    DIST_0_5  = config["hand.measurements"]["dist_0_5"]
    DIST_5_17 = config["hand.measurements"]["dist_5_17"]
    DIST_0_17 = config["hand.measurements"]["dist_0_17"]

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

