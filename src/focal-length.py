import cv2 as cv
from detectors import *
import methods


def pixel_dist_to_real_dist():

    return

def pixel_dist_to_real_depth():

    return


def main():

    real_depth = float(input("Real hand depth (mm): "))
    real_5_17 = float(input("Real distance between landmarks 5 and 17 (mm): "))

    assumed_0_5  = 0
    assumed_0_17 = 0

    handDetector = HandDetector()
    faceDetector = FaceDetector()

    cap = cv.VideoCapture(1)
    # cap.set(cv.CAP_PROP_FRAME_WIDTH,  1280)
    # cap.set(cv.CAP_PROP_FRAME_HEIGHT, 720)

    while 1:
        res, img = cap.read()

        if res == False:
            continue

        handDetector.detect(img)
        img = handDetector.draw(img, True, real_depth, real_5_17)

        faceDetector.detect(img)
        img = faceDetector.draw(img)

        cv.imshow("Image", img)
        if cv.waitKey(1) == 27:
            break


main()