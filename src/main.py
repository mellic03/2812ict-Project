import idk
from OpenGL.GL import *
import glm as glm

from sdl2 import *
from sdl2.sdlimage import *
import sdl2.ext

import threading
import cv2 as cv
import numpy as np

from detectors import *
from handrenderer import HandRenderer
from facerenderer import FaceRenderer

from sclient import *



NUM_USERS = 2


def net_thread_fn( netverts: list[np.ndarray] ):
    HOST = "127.0.0.1"
    PORT = 4200

    print("connecting to %s:%d" % (HOST, PORT), end="... ")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))
    print("connected")

    while True:
        if len(netverts) < NUM_USERS:
            continue

        message = sock.recv(128).decode("utf-8")
        print("[server >> client]: ", message)

        if message == "VERTS":
            print("Sending face vertices...")
            send_verts(netverts[0], sock)
            continue

        elif message == "END":
            print("Terminating")
            break


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



def gl_thread_fn( ren: idk.Renderer, handDetector: HandDetector, faceDetector: FaceDetector, netverts: list[np.ndarray]):

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

    netverts: list[np.ndarray] = [ ]

    t1 = threading.Thread(target=gl_thread_fn,  args=(ren, handDetector, faceDetector, netverts, ))
    t2 = threading.Thread(target=cv_thread_fn,  args=(ren, handDetector, faceDetector,))
    t3 = threading.Thread(target=net_thread_fn, args=(netverts,))

    t1.start()
    t2.start()
    t3.start()

    t1.join()
    t2.join()
    t3.join()



if __name__ == "__main__":
    main()

