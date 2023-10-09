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
from handcontroller import HandController
from facerenderer import FaceRenderer
from facecontroller import FaceController

import methods

import definitions as defs
import sys


def preprocess_img( img ):

    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    lap = cv.Laplacian(gray, -1, ksize=5, scale=1, delta=0, borderType=cv.BORDER_DEFAULT)
    lap = cv.cvtColor(lap, cv.COLOR_GRAY2BGR)

    lap = cv.resize(lap, (0, 0), fx=0.5, fy=0.5, interpolation=cv.INTER_LINEAR)
    lap = cv.GaussianBlur(lap, (7, 7), 0)

    lap = cv.resize(lap, (0, 0), fx=2, fy=2, interpolation=cv.INTER_LINEAR)
    lap = cv.GaussianBlur(lap, (3, 3), 0)

    lap = np.uint8(lap / 4)

    return img



def cv_thread_fn( ren: idk.Renderer, handDetector: HandDetector, faceDetector: FaceDetector ):
    cap = cv.VideoCapture("hand1.jpg")
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

    idk.loadPrimitive(idk.PRIMITIVE_UVSPHERE, "models/uvsphere.obj")
    idk.loadPrimitive(idk.PRIMITIVE_CYLINDER, "models/cylinder.obj")
    idk.loadPrimitive(idk.PRIMITIVE_CUBE, "models/cube.obj")

    plaincolor_shader = idk.compileShaderProgram("src/shaders/", "general.vs", "plaincolor.fs")
    idk.storeProgram("plaincolor", plaincolor_shader)

    cam = idk.Camera(80.0, width/height, 0.1, 1000.0)
    cam.translate(glm.vec3(0, 1.5, 0))
    cam.yaw(3.14159)

    texshader = idk.compileShaderProgram("src/shaders/", "general.vs", "textured.fs")

    grass_mh    = idk.loadOBJ(b"models/grass.obj", b"textures/grass.png")
    demoroom_mh = idk.loadOBJ(b"models/report.obj", b"textures/report.png")
    sky_mh      = idk.loadOBJ(b"models/skybox.obj", b"textures/skybox.png")
    cockpit_mh  = idk.loadOBJ(b"models/cockpit.obj", b"textures/palette.png")


    handRenderer_L  = HandRenderer("config/hand.ini")
    handRenderer_R  = HandRenderer("config/hand.ini")
    handController_L = HandController()
    handController_R = HandController()

    faceRenderer   = FaceRenderer("config/fRenderer.ini")
    faceController = FaceController("config/fController.ini")


    dtime = SDL_GetTicks64()
    start = SDL_GetTicks64()

    while (ren.running()):

        if dtime > 1/60:
            start = SDL_GetTicks64()

            ren.beginFrame(cam)

            glUseProgram(texshader)
            idk.setmat4(texshader, "un_proj", cam.projection())
            idk.setmat4(texshader, "un_view", cam.viewMatrix())
            idk.setvec3(texshader, "un_view_pos", cam.position())
            idk.setmat4(texshader, "un_model", glm.mat4(1.0))

            idk.drawVerticesTextured(texshader, sky_mh)
            idk.drawVerticesTextured(texshader, grass_mh)
            idk.drawVerticesTextured(texshader, cockpit_mh)


            handRenderer_L.draw(handDetector, cam, "Left")
            handRenderer_R.draw(handDetector, cam, "Right")
            handController_L.update(handRenderer_L, cam, dtime)
            handController_R.update(handRenderer_R, cam, dtime)

            faceRenderer.draw(faceDetector, cam, dtime)
            faceController.update(faceRenderer, cam)


            state = sdl2.SDL_GetKeyboardState(None)
            cam.onEvent(state, dtime)
            faceRenderer.onEvent(state, dtime)
            faceController.onEvent(state, dtime)


            # Make hand follow camera
            # ----------------------------------------------------------------------------------
            view = cam.viewMatrix()
            yaw = np.arctan2(view[2][0], view[0][0])


            handRenderer_L.setRotation(glm.rotate(-yaw, glm.vec3(0, 1, 0)))
            handRenderer_L.setTranslation(glm.translate(cam.position()))

            handRenderer_R.setRotation(glm.rotate(-yaw, glm.vec3(0, 1, 0)))
            handRenderer_R.setTranslation(glm.translate(cam.position()))
            # ----------------------------------------------------------------------------------


            # Make dist(model_hand, 3D_camera) ~= dist(real_hand, real_camera)
            # ----------------------------------------------------------------------------------
            face_depth = faceController.calculateDepth()
            hand_depth = handRenderer_L.calculateDepth()
            handRenderer_L.depthCorrection(glm.clamp(-(face_depth - hand_depth), -math.inf, -0.1))

            hand_depth = handRenderer_R.calculateDepth()
            handRenderer_R.depthCorrection(glm.clamp(-(face_depth - hand_depth), -math.inf, -0.1))
            # ----------------------------------------------------------------------------------


            # Visualise face direction
            # ----------------------------------------------------------------------------------
            center = 0.5*glm.vec3(6, -1.5, -2) + faceController.center()

            dir = glm.normalize(faceController.front())
            dir.z *= -1.0
            zpos = glm.vec3(0, 0, 1)

            methods.render_vector(center, dir, color = dir)
            methods.render_vector(center, zpos, color = zpos)
            methods.render_vector(center + 0.5*zpos, dir - zpos, color = dir - zpos)
            # ----------------------------------------------------------------------------------


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
    config.read("config/measurements.ini")

    defs.FOCAL_LENGTH             = float(config["camera"]["scaled-focal-length"])
    defs.DIST_0_5_mm              = float(config["hand"]["dist-0_5-mm"])
    defs.DIST_0_17_mm             = float(config["hand"]["dist-0_17-mm"])
    defs.DIST_5_17_mm             = float(config["hand"]["dist-5_17-mm"])
    defs.DIST_LEYE_REYE_mm        = float(config["face"]["dist-leye_reye-mm"])
    defs.DIST_MIDBROW_PHILTRUM_mm = float(config["face"]["dist-midbrow_philtrum-mm"])


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

