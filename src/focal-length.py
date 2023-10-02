import cv2 as cv
from detectors import *



def main():

    real_depth = float(input("Real hand depth (mm): "))
    real_5_17 = float(input("Real distance between landmarks 5 and 17 (mm): "))


    handDetector = HandDetector()

    cap = cv.VideoCapture(1)
    # cap.set(cv.CAP_PROP_FRAME_WIDTH,  1280)
    # cap.set(cv.CAP_PROP_FRAME_HEIGHT, 720)

    while 1:
        res, img = cap.read()

        if res == False:
            continue

        handDetector.detect(img)
        img = handDetector.draw(img, True, real_depth, real_5_17)

        cv.imshow("Image", img)
        cv.waitKey(1)



main()