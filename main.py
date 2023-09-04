# OpenGL -------------------------------------------
# This program requires a python wrapper for OpenGL
# along with SDL2, numpy and ctypes.
# pip install ctypes numpy pysdl2 PyOpenGL PyOpenGL_accelerate
# --------------------------------------------------
from renderer import Renderer
from renderer import Model
from OpenGL.GL import *
import glm as glm

from pprint import pprint

import threading
import cv2 as cv
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision


ren = Renderer(b"window", 1500, 1200, False )
results = None
img_w = None
img_h = None


def cv_thread_fn():
    cap = cv.VideoCapture(0)
    mpHands = mp.solutions.hands

    hands = mpHands.Hands(
        static_image_mode=False,
        max_num_hands=2,
        min_detection_confidence=0.25,
        min_tracking_confidence=0.25
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
                for id, lm in enumerate(handLms.landmark):
                    h, w, c = img.shape
                    cx, cy = int(lm.x *w), int(lm.y*h)
                    cv.circle(img, (cx,cy), 3, (255, 0, 255), cv.FILLED)

                mpDraw.draw_landmarks(img, handLms, mpHands.HAND_CONNECTIONS)

        cv.imshow("Image", img)
        cv.waitKey(1)


JOINT_LISTS = [
    [0, 1, 2, 3, 4],
    [1, 5],
    [0, 5, 6, 7, 8],
    [5, 9],
    [9, 10, 11, 12],
    [9, 13],
    [13, 14, 15, 16],
    [13, 17],
    [0, 17, 18, 19, 20]
]


def gl_thread_fn():

    width = 1500
    height = 1200
    ren.ren_init()

    proj = glm.perspective(80.0, width/height, 1, 100)

    uvsphere = Model()
    uvsphere_h = uvsphere.loadOBJ(b"models/cube/", b"icosphere.obj", b"cube.mtl", b"container.png")

    unit = Model()
    unit_h = unit.loadOBJ(b"models/cube/", b"cube.obj", b"cube.mtl", b"container.png")

    cube = Model()
    cube_h = cube.loadOBJ(b"models/cube/", b"cube.obj", b"cube.mtl", b"container.png")

    basic_shader: GLuint = ren.compileShaderProgram("./", "basic.vs", "basic.fs")
    tex_shader: GLuint = ren.compileShaderProgram("./", "textured.vs", "textured.fs")

    trans1 = glm.translate(glm.mat4(1.0), glm.vec3( 2.0, 0.0, -6.0))
    trans2 = glm.translate(glm.mat4(1.0), glm.vec3(-2.0, 0.0, -4.0))


    theta = 0
    while (ren.running()):
        ren.beginFrame()

        rot = glm.rotate(3.1415, glm.vec3(0.0, 0.0, 1.0))
        rot = glm.rotate(theta, glm.vec3(0.0, 1.0, 0.0)) * rot

        global img_w
        global img_h
        global results
        if results and results.multi_hand_landmarks:
            glUseProgram(basic_shader)
            ren.setmat4(basic_shader, "proj", proj)

            for handLms in results.multi_hand_landmarks:
                # Get delta_pos between joint and write
                wrist = handLms.landmark[mp.solutions.hands.HandLandmark.WRIST]

                for joint_list in JOINT_LISTS:
                    for i in range(0, len(joint_list)-1):
                        a = handLms.landmark[joint_list[i]]
                        b = handLms.landmark[joint_list[i+1]]

                        pos_u = glm.vec3(8*(img_w/img_h)*(a.x-0.5), 8*(a.y-0.5),  10*wrist.z + -3.5+10*a.z)
                        pos_v = glm.vec3(8*(img_w/img_h)*(b.x-0.5), 8*(b.y-0.5),  10*wrist.z + -3.5+10*b.z)

                        dist = glm.length(pos_v - pos_u)

                        pos_scale = glm.translate(glm.vec3(0.0, 0.0, -dist)) * glm.scale(glm.vec3(0.3, 0.3, 2*dist))
                        pos_rot = glm.inverse(glm.lookAt(pos_u, pos_v, glm.vec3(0.0, 1.0, 0.0)))
                        pos_trans = glm.translate(pos_u)

                        ren.setmat4(basic_shader, "model", pos_trans*pos_rot*pos_scale)
                        ren.setvec3(basic_shader, "un_color", glm.vec3(1.0, 1.0-(i*0.15), 1.0-(i*0.15)))
                        ren.drawVertices(unit_h)

                # for id, lm in enumerate(handLms.landmark):
                #     pos = [8*(img_w/img_h)*(lm.x-0.5), 8*(lm.y-0.5), 10*wrist.z + -3.5+10*lm.z ]

                #     scale = glm.scale(glm.vec3(0.1, 0.1, 0.1))
                #     trans = glm.translate(glm.vec3(pos[0], pos[1], pos[2]))

                #     ren.setmat4(basic_shader, "model", trans*scale)
                #     ren.drawVertices(uvsphere_h)


        # glUseProgram(tex_shader)
        # ren.setmat4(tex_shader, "proj", proj)
        # ren.setmat4(tex_shader, "model", trans1*rot)
        # ren.drawVerticesTextured(tex_shader, cube_h)

        theta += 0.01
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

