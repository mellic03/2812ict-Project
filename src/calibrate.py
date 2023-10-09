import cv2 as cv
from detectors import *
import glm
import methods
import configparser


LBROW_IDX = 223
RBROW_IDX = 443
LEYE_IDX  = 33
REYE_IDX  = 263

MIDBROW_IDX  = 168
PHILTRUM_IDX = 164


def ndc_to_pixel( ndc, shape ) -> glm.vec2:
    return glm.vec2(ndc.x * shape[1], ndc.y * shape[0])



class HandFaceRatio:

    def __init__(self, real_depth_mm, real_h_0_17_mm) -> None:

        self.depth_real    = real_depth_mm
        self.h_0_17_real   = real_h_0_17_mm
        self.h_0_17_pxl    = 0
        self.h_0_5_est     = 0
        self.h_5_17_est    = 0
        self.leye_reye_est = 0
        self.mid_phil_est  = 0

        self.focal_est     = 1
        self.num_samples   = 0


    def __add_hand_sample(self, img, hd: HandDetector):
        results = hd.results()
        if not results or not results.multi_hand_landmarks:
            return

        handlms = None
        for handLms in results.multi_hand_landmarks:
            handlms = handLms
            break

        lm0  = ndc_to_pixel(handlms.landmark[0], img.shape)
        lm5  = ndc_to_pixel(handlms.landmark[5], img.shape)
        lm17 = ndc_to_pixel(handlms.landmark[17], img.shape)

        self.h_0_17_pxl += glm.distance(lm0, lm17)
        h_0_5_pxl        = glm.distance(lm0, lm5)
        h_5_17_pxl       = glm.distance(lm5, lm17)

        self.h_0_5_est  += methods.pixel_dist_to_real_dist(
            self.h_0_17_real, self.h_0_17_pxl/self.num_samples, h_0_5_pxl
        )

        self.h_5_17_est += methods.pixel_dist_to_real_dist(
            self.h_0_17_real, self.h_0_17_pxl/self.num_samples, h_5_17_pxl
        )
        


    def __add_face_sample(self, img, fd: FaceDetector):
        results = fd.results()
        if not results or not results.multi_face_landmarks:
            return

        facelms = None
        for faceLms in results.multi_face_landmarks:
            facelms = faceLms
            break

        leye = ndc_to_pixel(facelms.landmark[LEYE_IDX], img.shape)
        reye = ndc_to_pixel(facelms.landmark[REYE_IDX], img.shape)

        philtrum = ndc_to_pixel(facelms.landmark[PHILTRUM_IDX], img.shape)
        midbrow  = ndc_to_pixel(facelms.landmark[MIDBROW_IDX], img.shape)

        leye_reye_pxl = glm.distance(leye, reye)
        mid_phil_pxl  = glm.distance(midbrow, philtrum)

        self.leye_reye_est += methods.pixel_dist_to_real_dist(
            self.h_0_17_real, self.h_0_17_pxl/self.num_samples, leye_reye_pxl
        )

        self.mid_phil_est += methods.pixel_dist_to_real_dist(
            self.h_0_17_real, self.h_0_17_pxl/self.num_samples, mid_phil_pxl
        )


    def addSample(self, img, hd: HandDetector, fd: FaceDetector):
        self.num_samples += 1
        self.__add_hand_sample(img, hd)
        self.__add_face_sample(img, fd)


    def __div_config(self, config, name):
        for key in config[name]:
            value = float(config[name][key]) / self.num_samples
            config[name][key] = str(value)


    def __writeINI_camera(self, config):
        smp = self.num_samples

        focal_dist = methods.estimate_scaled_focal_length(
            self.depth_real, self.h_0_17_real, self.h_0_17_pxl/smp
        )
        config["camera"] = {
            "scaled-focal-length": focal_dist
        }


    def __writeINI_hand(self, config):
        config["hand"] = {
            "dist-0_5-mm":      self.h_0_5_est   / self.num_samples,
            "dist-0_17-mm":     self.h_0_17_real,
            "dist-5_17-mm":     self.h_5_17_est  / self.num_samples,
            "ratio-0_5-5_17":   self.h_0_5_est / self.h_5_17_est
        }


    def __writeINI_face(self, config):
        config["face"] = {
            "dist-leye_reye-mm":        self.leye_reye_est / self.num_samples,
            "dist-midbrow_philtrum-mm": self.mid_phil_est  / self.num_samples,
            "ratio-WxH":                self.mid_phil_est / self.leye_reye_est
        }


    def writeINI(self, filepath: str):
        config = configparser.ConfigParser()

        self.__writeINI_camera(config)
        self.__writeINI_hand(config)
        self.__writeINI_face(config)

        fh = open(filepath, "w")
        config.write(fh)
        fh.close()



def draw_face_roll( img, leye, reye, good=False ):

    color_A = (255, 0, 50) if not good else (0, 255, 0)
    color_B = (50, 0, 255) if not good else (0, 255, 0)

    cv.line( img,
        (int(leye.x),  int(leye.y)),
        (int(reye.x),  int(leye.y)),
        color_A, thickness=2
    )

    cv.line( img,
        (int(reye.x),  int(reye.y)),
        (int(leye.x),  int(reye.y)),
        color_B, thickness=2
    )



def draw_face_yaw( img, leye, philtrum, reye, good=False ):

    color_A = (255, 0, 50) if not good else (0, 255, 0)
    color_B = (50, 0, 255) if not good else (0, 255, 0)


    # left eye <---> midface
    # -------------------------------------------------------
    cv.line( img,
        (int(leye.x),      int(philtrum.y)),
        (int(philtrum.x),  int(philtrum.y)),
        color_A, thickness=2
    )

    cv.line( img,
        (int(leye.x),  int(leye.y)),
        (int(leye.x),  int(philtrum.y)),
        color_B, thickness=2
    )

    cv.line( img,
        (int(leye.x),  int(leye.y)),
        (int(philtrum.x),  int(philtrum.y)),
        (0, 0, 0), thickness=1
    )
    # -------------------------------------------------------

    # right eye <---> midface
    # -------------------------------------------------------
    cv.line( img,
        (int(reye.x),      int(philtrum.y)),
        (int(philtrum.x),  int(philtrum.y)),
        color_B, thickness=2
    )

    cv.line( img,
        (int(reye.x),  int(reye.y)),
        (int(reye.x),  int(philtrum.y)),
        color_A, thickness=2
    )

    cv.line( img,
        (int(reye.x),  int(reye.y)),
        (int(philtrum.x),  int(philtrum.y)),
        (0, 0, 0), thickness=1
    )
    # -------------------------------------------------------



def evaluate_face_roll( img, leye, reye, draw=False ) -> tuple[bool, float]:

    # leye.y should rougly equal reye.y for roll alignment

    EPSILON = 0.05 # Allow 5% tolerance

    roll_fitness = math.fabs(leye.y - reye.y)
    roll_good    = roll_fitness <= 1

    if draw:
        draw_face_roll(img, leye, reye, roll_good)

    return roll_good, roll_fitness



def evaluate_face_yaw( img, leye, reye, philtrum, draw=False ) -> tuple[bool, float]:

    # dist(leye midbrow) should roughly equal dist(reye, midbrow) for yaw alignment.

    EPSILON = 0.05 # Allow 5% tolerance

    leye_philtrum_xdist = math.fabs(leye.x - philtrum.x)
    reye_philtrum_xdist = math.fabs(philtrum.x - reye.x)

    min_dist = min([leye_philtrum_xdist, reye_philtrum_xdist])
    max_dist = max([leye_philtrum_xdist, reye_philtrum_xdist])

    yaw_fitness = (min_dist / max_dist)
    yaw_good    = (1.0 + EPSILON) * yaw_fitness >= 1

    if draw:
        draw_face_yaw(img, leye, philtrum, reye, yaw_good)

    return yaw_good, yaw_fitness



def evaluate_face_alignment( img, fd: FaceDetector ):

    results = fd.results()
    if not results or not results.multi_face_landmarks:
        return None, None

    for facelms in results.multi_face_landmarks:

        leye = ndc_to_pixel(facelms.landmark[LEYE_IDX], img.shape)
        reye = ndc_to_pixel(facelms.landmark[REYE_IDX], img.shape)

        philtrum = ndc_to_pixel(facelms.landmark[PHILTRUM_IDX], img.shape)
        midbrow  = ndc_to_pixel(facelms.landmark[MIDBROW_IDX], img.shape)

        roll_good, roll_fitness = evaluate_face_roll(img, leye, reye, True)
        yaw_good,  yaw_fitness  = evaluate_face_yaw(img, leye, reye, philtrum, True)

        # print("roll=%.2f,    yaw=%.2f" % (roll_value, yaw_value))

        return roll_good, yaw_good



def draw_hand_roll( img, lm0, lm5, lm17, good=False ):

    color_A = (255, 0, 50) if not good else (0, 255, 0)
    color_B = (50, 0, 255) if not good else (0, 255, 0)

    cv.line( img,
        (int(lm17.x),   int(lm17.y)),
        (int(lm17.x),   int(lm0.y)),
        color_A, thickness=2
    )

    cv.line( img,
        (int(lm0.x),   int(lm0.y)),
        (int(lm0.x),   int(lm17.y)),
        color_B, thickness=2
    )



def evaluate_hand_roll( img, lm0, lm5, lm17, draw=False ) -> tuple[bool, float]:

    EPSILON = 0.01 * img.shape[1]

    roll_fitness = math.fabs(lm0.x - lm17.x)
    roll_good  = -EPSILON <= roll_fitness <= +EPSILON

    if draw:
        draw_hand_roll(img, lm0, lm5, lm17, roll_good)

    return roll_good, roll_fitness



def evaluate_hand_alignment( img, hd: HandDetector ):

    results = hd.results()
    if not results or not results.multi_hand_landmarks:
        return None

    for handLms in results.multi_hand_landmarks:

        lm0  = ndc_to_pixel(handLms.landmark[0], img.shape)
        lm5  = ndc_to_pixel(handLms.landmark[5], img.shape)
        lm17 = ndc_to_pixel(handLms.landmark[17], img.shape)

        roll_good, roll_fitness = evaluate_hand_roll(img, lm0, lm5, lm17, True)

        return roll_good


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

