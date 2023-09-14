import idk
from OpenGL.GL import *
import glm as glm

from sdl2 import *
from sdl2.sdlimage import *
import sdl2.ext

import threading
import cv2 as cv
import numpy as np
import client

from detectors import *
from handrenderer import HandRenderer
from facerenderer import FaceRenderer


def cv_thread_fn( ren: idk.Renderer, handDetector: HandDetector, faceDetector: FaceDetector ):

    cap = cv.VideoCapture(0,)
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



def gl_thread_fn( ren: idk.Renderer, handDetector: HandDetector, faceDetector: FaceDetector ):

    client.init(b"127.0.0.1", 4200)
    print("userid: ", client.get_userid())

    width = 1500
    height = 1200
    ren.ren_init()
    glDisable(GL_CULL_FACE)
    SDL_GL_SetSwapInterval(0)

    cam = idk.Camera(80.0, width/height, 0.1, 10000.0)
    cam.translate(glm.vec3(-1.0, -1.0, -1.0))
    cam.yaw(glm.radians(180))

    room = idk.Model()

    sky = idk.Model()
    sky_mh = sky.loadOBJ(b"models/skybox.obj", b"textures/skybox.png")
    sky_shader = idk.compileShaderProgram("src/shaders/", "general.vs", "skybox.fs")

    grass = idk.Model()
    grass_mh = grass.loadOBJ(b"models/grass.obj", b"textures/grass.png")
    grass_shader = idk.compileShaderProgram("src/shaders/", "general.vs", "textured.fs")

    handRenderer = HandRenderer("config/hand.ini")
    faceRenderer = FaceRenderer("config/face.ini")


    dtime = SDL_GetTicks64()

    while (ren.running()):

        start = SDL_GetTicks64()

        ren.beginFrame(cam)

        glUseProgram(sky_shader)
        idk.setmat4(sky_shader, "un_proj", cam.projection())
        idk.setmat4(sky_shader, "un_view", cam.viewMatrix())
        idk.setmat4(sky_shader, "un_model", glm.mat4(1.0))
        idk.drawVerticesTextured(sky_shader, sky_mh)

        glUseProgram(grass_shader)
        idk.setmat4(grass_shader, "un_proj", cam.projection())
        idk.setmat4(grass_shader, "un_view", cam.viewMatrix())
        idk.setmat4(grass_shader, "un_model", glm.mat4(1.0))
        idk.setvec3(grass_shader, "un_view_pos", cam.position())
        idk.setfloat(grass_shader, "un_spec_exponent", 4)
        idk.setfloat(grass_shader, "un_spec_strength", 0.1)
        idk.drawVerticesTextured(grass_shader, grass_mh)


        handRenderer.draw(handDetector, cam)
        faceRenderer.draw(faceDetector, cam, dtime)

        state = sdl2.SDL_GetKeyboardState(None)
        cam.onEvent(state, dtime)
        faceRenderer.onEvent(state)

        ren.endFrame()

        dtime = (SDL_GetTicks64() - start) / 1000.0



def main():
    ren = idk.Renderer(b"window", 1500, 1200, False )
    handDetector = HandDetector()
    faceDetector = FaceDetector()

    t1 = threading.Thread(target=gl_thread_fn,  args=(ren, handDetector, faceDetector,))
    t2 = threading.Thread(target=cv_thread_fn,  args=(ren, handDetector, faceDetector,))

    t1.start()
    t2.start()

    t1.join()
    t2.join()



if __name__ == "__main__":
    main()

