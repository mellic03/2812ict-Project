# OpenGL -------------------------------------------
# This program requires a python wrapper for OpenGL
# along with SDL2, numpy and ctypes.
# pip install ctypes numpy pysdl2 PyOpenGL PyOpenGL_accelerate
# --------------------------------------------------
import idk
from OpenGL.GL import *
import glm as glm

from pprint import pprint

import threading
import numpy as np
import cv2 as cv
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import math

ren = idk.Renderer(b"window", 1500, 1200, False )
results = None
img_w = None
img_h = None



# Data points for a polynomial regression
x = [300, 245, 200, 170, 145, 130, 112, 103, 93, 87, 80, 75, 70, 67, 62, 59, 57]
y = [20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100]
coff = np.polyfit(x, y, 2)  # y = Ax^2 + Bx + C


def cv_thread_fn():
    cap = cv.VideoCapture(0)
    cap.set(cv.CAP_PROP_FRAME_WIDTH,  640)
    cap.set(cv.CAP_PROP_FRAME_HEIGHT, 480)
    mpHands = mp.solutions.hands

    hands = mpHands.Hands(
        static_image_mode=False,
        max_num_hands=2,
        min_detection_confidence=0.9,
        min_tracking_confidence=0.9
    )

    # print(mp.solutions.hands.HandLandmark.WRIST)

    mpDraw = mp.solutions.drawing_utils
    res, img = cap.read()

    global img_w
    global img_h
    img_w = img.shape[1]
    img_h = img.shape[0]

    while ren.running():
        res, img = cap.read()

        imgRGB = cv.cvtColor(img, cv.COLOR_BGR2RGB)
        global results
        results = hands.process(imgRGB)

        if results.multi_hand_landmarks:

            # global wrist
            # wrist = results.multi_hand_landmarks[0].landmark[1]

            for handLms in results.multi_hand_landmarks:
                mpDraw.draw_landmarks(img, handLms, mpHands.HAND_CONNECTIONS)
                # for id, lm in enumerate(handLms.landmark):
                #     h, w, c = img.shape
                #     cx, cy = int(lm.x *w), int(lm.y*h)
                #     cv.circle(img, (cx,cy), 5, (0, 255, 0), cv.FILLED)

        cv.imshow("Image", img)
        cv.waitKey(1)


JOINT_LISTS = [
    [0, 1, 2, 3, 4],
    [1, 5],
    [0, 9],
    [0, 13],
    [0, 5, 6, 7, 8],
    [5, 9],
    [9, 10, 11, 12],
    [9, 13],
    [13, 14, 15, 16],
    [13, 17],
    [0, 17, 18, 19, 20]
]

FINGERTIPS = [ 4, 8, 12, 16, 20 ]

MY_HAND_DIST1_CM = 7
MY_HAND_DIST2_CM = 8


def calculate_distance(x1, y1, x2, y2):
    distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    return distance


def gl_thread_fn():

    width = 1500
    height = 1200
    ren.ren_init()
    cam = idk.Camera(80.0, width/height, 0.1, 100.0)
    cam.translate(glm.vec3(0.0, -1.0, 0.0))

    proj = glm.perspective(80.0, width/height, 0.1, 100)

    uvsphere = idk.Model()
    uvsphere_h = uvsphere.loadOBJ(b"models/cube/", b"icosphere.obj", b"cube.mtl", b"container.png")

    unit = idk.Model()
    unit_h = unit.loadOBJ(b"models/cube/", b"cylinder.obj", b"cube.mtl", b"container.png")

    cube = idk.Model()
    cube_h = cube.loadOBJ(b"models/cube/", b"cube.obj", b"cube.mtl", b"container.png")

    room = idk.Model()
    room_h = cube.loadOBJ(b"models/cube/", b"room.obj", b"cube.mtl", b"soy.png")


    basic_shader: GLuint = ren.compileShaderProgram("src/shaders/", "basic.vs", "basic.fs")
    tex_shader: GLuint = ren.compileShaderProgram("src/shaders/", "textured.vs", "textured.fs")

    trans1 = glm.translate(glm.mat4(1.0), glm.vec3( 0.0, 0.0, -4.0))
    trans2 = glm.translate(glm.mat4(1.0), glm.vec3(-2.0, 0.0, -4.0))

    # 280pixels --> 16.0cm
    CMPP = 16.0 / 280

    while (ren.running()):
        ren.beginFrame()

        glUseProgram(basic_shader)
        ren.setmat4(basic_shader, "un_view", cam.viewMatrix())
        ren.setvec3(basic_shader, "un_view_pos", cam.position())
        ren.setmat4(basic_shader, "proj", proj)

        global img_w
        global img_h
        global results
        if results and results.multi_hand_landmarks:

            for (handLms, whandLms) in zip(results.multi_hand_landmarks, results.multi_hand_world_landmarks):

                x0 = handLms.landmark[5].x * img_w
                y0 = handLms.landmark[5].y * img_h
                x1 = handLms.landmark[17].x * img_w
                y1 = handLms.landmark[17].y * img_h
                pixel_dist1 = np.sqrt((x0-x1)**2 + (y0-y1)**2)

                x0 = handLms.landmark[5].x * img_w
                y0 = handLms.landmark[5].y * img_h
                pixel_dist2 = np.sqrt((x0-x1)**2 + (y0-y1)**2)

                A, B, C = coff
                hand_dist1 = A*pixel_dist1**2 + B*pixel_dist1 + C
                hand_dist2 = A*pixel_dist2**2 + B*pixel_dist2 + C

                hand_dist = min(hand_dist1, hand_dist2)
                hand_dist /= 100
                print(hand_dist)

                wrist = handLms.landmark[0]
                wrist = [(wrist.x-0.5), (wrist.y-0.75), wrist.z - 1.0 + hand_dist]

                for joint_list in JOINT_LISTS:
                    for i in range(0, len(joint_list)-1):
                        a = whandLms.landmark[joint_list[i]]
                        b = whandLms.landmark[joint_list[i+1]]

                        SCALE = 1

                        pos_u = glm.vec3(SCALE*(wrist[0]+a.x), SCALE*(wrist[1]+a.y), wrist[2] + SCALE*(a.z))
                        pos_v = glm.vec3(SCALE*(wrist[0]+b.x), SCALE*(wrist[1]+b.y), wrist[2] + SCALE*(b.z))

                        dist = glm.length(pos_v - pos_u)


                        pos_scale = glm.translate(glm.vec3(0.0, 0.0, -dist)) * glm.scale(glm.vec3(0.03, 0.03, 2*dist))
                        pos_rot = glm.inverse(glm.lookAt(pos_u, pos_v, glm.vec3(0.0, 1.0, 0.0)))
                        pos_trans = glm.translate(pos_u + glm.vec3(0.0, 0.0, -0.4))
                        transform = pos_trans*pos_rot*pos_scale
                        if cam.coupled:
                            transform = glm.inverse(cam.viewMatrix()) * transform
                        ren.setmat4(basic_shader, "model", transform)
                        ren.setvec3(basic_shader, "un_color", glm.vec3(1.0, 1.0-(i*0.15), 1.0-(i*0.15)))
                        ren.drawVertices(unit_h)

                        # Knuckles
                        pos_scale = glm.scale(glm.vec3(0.03))
                        pos_trans = glm.translate(pos_u + glm.vec3(0.0, 0.0, -0.4))
                        transform = pos_trans*pos_rot*pos_scale
                        if cam.coupled:
                            transform = glm.inverse(cam.viewMatrix()) * transform
                        ren.setmat4(basic_shader, "model", transform)
                        ren.drawVertices(uvsphere_h)

                        # Fingertips
                        pos_scale = glm.translate(glm.vec3(0.0, 0.0, -dist)) * glm.scale(glm.vec3(0.03))
                        pos_trans = glm.translate(pos_v + glm.vec3(0.0, 0.0, -0.4))
                        transform = pos_trans*pos_rot*pos_scale
                        if cam.coupled:
                            transform = glm.inverse(cam.viewMatrix()) * transform
                        ren.setmat4(basic_shader, "model", transform)
                        ren.drawVertices(uvsphere_h)






        glUseProgram(tex_shader)
        ren.setmat4(tex_shader, "un_view", cam.viewMatrix())
        ren.setvec3(tex_shader, "un_view_pos", cam.position())
        ren.setvec3(tex_shader, "un_color", glm.vec3(1.0))
        ren.setmat4(tex_shader, "proj", proj)
        ren.setmat4(tex_shader, "model", trans1)
        ren.drawVerticesTextured(tex_shader, room_h)

        ren.processKeyEvents(cam)


        # theta += 0.01
        ren.endFrame()




def main():

    t1 = threading.Thread(target=gl_thread_fn)
    t2 = threading.Thread(target=cv_thread_fn)

    t1.start()
    t2.start()

    t1.join()
    t2.join()



if __name__ == "__main__":
    main()

