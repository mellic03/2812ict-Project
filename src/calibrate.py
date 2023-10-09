import cv2 as cv
from detectors import *
from calibration_methods import *


def main():

    real_0_17 = float(input("Real-world distance between hand landmarks 0 and 17 (mm): "))
    real_depth = float(input("Real-world distance between camera and face to be used for calibration (mm): "))

    handDetector = HandDetector()
    faceDetector = FaceDetector()

    cap = cv.VideoCapture(0)
    # cap.set(cv.CAP_PROP_FRAME_WIDTH,  1280)
    # cap.set(cv.CAP_PROP_FRAME_HEIGHT, 720)

    hfRatio = HandFaceRatio(real_depth, real_0_17)

    while 1:
        res, img = cap.read()

        if res == False:
            continue

        handDetector.detect(img)
        img = handDetector.draw(img)

        faceDetector.detect(img)
        img = faceDetector.draw(img)


        h_roll_good = evaluate_hand_alignment(img, handDetector)
        f_roll_good, f_yaw_good = evaluate_face_alignment(img, faceDetector)

        if h_roll_good and f_roll_good and f_yaw_good:
            hfRatio.addSample(img, handDetector, faceDetector)
            print("Samples: %d" % (hfRatio.num_samples))

        cv.imshow("Image", cv.flip(img, 1))

        key = cv.waitKey(1)

        if key == 27 or key == ord(' '):
            break

    hfRatio.writeINI("config/measurements.ini")


main()

