import idk
from OpenGL.GL import *
import glm as glm

from sdl2 import *
from sdl2.sdlimage import *
import sdl2.ext

import threading
import cv2 as cv
import numpy as np
import configparser

from detectors import *
from handrenderer import HandRenderer
from facerenderer import FaceRenderer
from facecontroller import FaceController

import definitions as defs
import sys


def preprocess_img( img ):

    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    lap = cv.Laplacian(gray, -1, ksize=5, scale=1, delta=0, borderType=cv.BORDER_DEFAULT)
    lap = cv.cvtColor(lap, cv.COLOR_GRAY2BGR)

    # lap = cv.resize(lap, (0, 0), fx=0.5, fy=0.5, interpolation=cv.INTER_LINEAR)
    # lap = cv.GaussianBlur(lap, (7, 7), 0)

    # lap = cv.resize(lap, (0, 0), fx=2, fy=2, interpolation=cv.INTER_LINEAR)
    # lap = cv.GaussianBlur(lap, (3, 3), 0)

    lap = np.uint8(lap / 2)

    return img



global hgrabbing
hgrabbing = False


def cv_thread_fn( ren: idk.Renderer, handDetector: HandDetector, faceDetector: FaceDetector ):
    cap = cv.VideoCapture(1)
    # cap.set(cv.CAP_PROP_FRAME_WIDTH,  1280)
    # cap.set(cv.CAP_PROP_FRAME_HEIGHT, 720)

    while ren.running():
        res, img = cap.read()

        if res == False:
            continue

        img = preprocess_img(img)

        defs.IMG_H = img.shape[0]
        defs.IMG_W = img.shape[1]

        faceDetector.detect(img)
        img = faceDetector.draw(img)

        global hgrabbing
        handDetector.grabbing = hgrabbing

        handDetector.detect(img)
        img = handDetector.draw(img)

        cv.imshow("Image", img)
        cv.waitKey(1)



def gl_thread_fn( ren: idk.Renderer, handDetector: HandDetector, faceDetector: FaceDetector ):

    width = 1500
    height = 1200
    ren.ren_init()
    glDisable(GL_CULL_FACE)
    glEnable(GL_MULTISAMPLE)

    SDL_GL_SetSwapInterval(0)
    cam = idk.Camera(80.0, width/height, 0.1, 1000.0)


    sky = idk.Model()
    sky_mh = sky.loadOBJ(b"models/skybox.obj", b"textures/skybox.png")
    sky_shader = idk.compileShaderProgram("src/shaders/", "general.vs", "skybox.fs")

    grass = idk.Model()
    grass_mh = grass.loadOBJ(b"models/report.obj", b"textures/report.png")
    grass_shader = idk.compileShaderProgram("src/shaders/", "general.vs", "textured.fs")

    cockpit = idk.Model()
    cockpit_mh = cockpit.loadOBJ(b"models/cockpit.obj", b"textures/palette.png")

    handRenderer_L = HandRenderer("config/hand.ini")
    handRenderer_R = HandRenderer("config/hand.ini")
    faceRenderer   = FaceRenderer("config/fRenderer.ini")
    faceController = FaceController("config/fController.ini")


    dtime = SDL_GetTicks64()
    start = SDL_GetTicks64()

    while (ren.running()):

        if dtime > 1/60:
            start = SDL_GetTicks64()

            ren.beginFrame(cam)

            # Render background
            # ---------------------------------------------------------
            glUseProgram(sky_shader)
            idk.setmat4(sky_shader, "un_proj", cam.projection())
            idk.setmat4(sky_shader, "un_view", cam.viewMatrix())
            idk.setmat4(sky_shader, "un_model", glm.mat4(1.0))
            idk.drawVerticesTextured(sky_shader, sky_mh)
            # ---------------------------------------------------------

            # Render terrain
            # ---------------------------------------------------------
            glUseProgram(grass_shader)
            idk.setmat4(grass_shader, "un_proj", cam.projection())
            idk.setmat4(grass_shader, "un_view", cam.viewMatrix())
            idk.setmat4(grass_shader, "un_model", glm.mat4(1.0))
            idk.setvec3(grass_shader, "un_view_pos", cam.position())
            idk.setfloat(grass_shader, "un_spec_exponent", 4)
            idk.setfloat(grass_shader, "un_spec_strength", 0.1)
            idk.drawVerticesTextured(grass_shader, grass_mh)
            # ---------------------------------------------------------

            # Cockpit
            # ---------------------------------------------------------
            # glUseProgram(grass_shader)
            # idk.setmat4(sky_shader, "un_proj", cam.projection())
            # idk.setmat4(sky_shader, "un_view", cam.viewMatrix())

            # rotation = glm.rotate(glm.radians(-90), glm.vec3(0.0, 1.0, 0.0))
            # translation = glm.translate(glm.vec3(10.0, -3.0, 0.0))
            # idk.setmat4(sky_shader, "un_model", translation * rotation)
            # idk.drawVerticesTextured(grass_shader, cockpit_mh)
            # ---------------------------------------------------------


            handRenderer_L.draw(handDetector, cam, "Left")
            handRenderer_R.draw(handDetector, cam, "Right")
            faceRenderer.draw(faceDetector, cam, dtime)
            faceController.update(faceRenderer, cam)

            global hgrabbing
            hgrabbing = handRenderer_L.grabbing

            state = sdl2.SDL_GetKeyboardState(None)
            cam.onEvent(state, dtime)
            faceRenderer.onEvent(state, dtime)
            faceController.onEvent(state, dtime)

            ren.endFrame()


        dtime = (SDL_GetTicks64() - start) / 1000.0



def main():
    if len(sys.argv) > 1 and sys.argv[1] == "USE_CPP":
        defs.USE_Python = False
        defs.USE_CPP    = True
    else:
        defs.USE_PYTHON = True
        defs.USE_CPP    = False

    config = configparser.ConfigParser()
    config.read("config/camera.ini")
    defs.FOCAL_LENGTH = float(config["specifications"]["focal-length"])

    ren = idk.Renderer(b"window", 1500, 1200, False )
    handDetector = HandDetector()
    faceDetector = FaceDetector()

    t1 = threading.Thread(target=gl_thread_fn,  args=(ren, handDetector, faceDetector,))
    t2 = threading.Thread(target=cv_thread_fn,  args=(ren, handDetector, faceDetector,))
    t2.daemon = True

    t1.start()
    t2.start()

    t1.join()
    t2.join()




if __name__ == "__main__":
    main()

