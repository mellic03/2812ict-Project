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
        self.h_0_17_pxl    = math.inf
        self.h_0_5_est     = math.inf
        self.h_5_17_est    = math.inf
        self.leye_reye_est = math.inf
        self.mid_phil_est  = math.inf

        self.focal_est     = 1


    def __update_hand_distances(self, img, hd: HandDetector):
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

        self.h_0_17_pxl = glm.distance(lm0, lm17)
        h_0_5_pxl  = glm.distance(lm0, lm5)
        h_5_17_pxl = glm.distance(lm5, lm17)

        self.h_0_5_est  = methods.pixel_dist_to_real_dist(
            self.h_0_17_real, self.h_0_17_pxl, h_0_5_pxl
        )

        self.h_5_17_est = methods.pixel_dist_to_real_dist(
            self.h_0_17_real, self.h_0_17_pxl, h_5_17_pxl
        )
        


    def __update_face_distances(self, img, fd: FaceDetector):
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

        self.leye_reye_est = methods.pixel_dist_to_real_dist(
            self.h_0_17_real, self.h_0_17_pxl, leye_reye_pxl
        )

        self.mid_phil_est = methods.pixel_dist_to_real_dist(
            self.h_0_17_real, self.h_0_17_pxl, mid_phil_pxl
        )


    def updatePixelDistances(self, img, hd: HandDetector, fd: FaceDetector):
        self.__update_hand_distances(img, hd)
        self.__update_face_distances(img, fd)


    def __writeINI_camera(self, config):

        focal_dist = methods.estimate_scaled_focal_length(
            self.depth_real, self.h_0_17_real, self.h_0_17_pxl
        )

        config["camera"] = {
            "scaled-focal-length": focal_dist
        }


    def __writeINI_hand(self, config):
        config["hand"] = {
            "dist-0-5-mm":  self.h_0_5_est,
            "dist-0-17-mm": self.h_0_17_real,
            "dist-5-17-mm": self.h_5_17_est,
            "ratio_0-5_5-17": self.h_0_5_est / self.h_5_17_est
        }


    def __writeINI_face(self, config):
        config["face"] = {
            "dist-leye-reye-mm":        self.leye_reye_est,
            "dist-midbrow-philtrum-mm": self.mid_phil_est,
            "ratio-width-by-height":    self.mid_phil_est / self.leye_reye_est
       
        }


    def writeINI(self, filepath: str):
        config = configparser.ConfigParser()

        self.__writeINI_camera(config)
        self.__writeINI_hand(config)
        self.__writeINI_face(config)

        fh = open(filepath, "w")
        config.write(fh)
        fh.close()



def draw_hand_lines( img, hd: HandDetector, real_depth_mm: float, real_0_17: float ) -> None:

    results = hd.results()

    if results and results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            hd.mpDraw.draw_landmarks(
                img,
                handLms,
                hd.hands.HAND_CONNECTIONS
            )
            
            x0  = int( img.shape[1] * handLms.landmark[0].x)
            x5  = int( img.shape[1] * handLms.landmark[5].x)
            x17 = int( img.shape[1] * handLms.landmark[17].x)

            y0  = int( img.shape[0] * handLms.landmark[0].y)
            y5  = int( img.shape[0] * handLms.landmark[5].y)
            y17 = int( img.shape[0] * handLms.landmark[17].y)

            color = (0, 0, 255)
            if math.fabs(y5-y17) < 5.0:
                color = (0, 255, 0)

            cv.line( img,
                (x5, y5),
                (x17, y5),
                color, thickness=5
            )

            cv.line( img,
                (x17, y17),
                (x5,  y17),
                color, thickness=5
            )
            
            pixel_0_17 = glm.distance([x0, y0], [x17, y17])

            focal_length = (real_depth_mm * pixel_0_17) / real_0_17

            cv.putText(img, "f: %.2f" % (focal_length), (10, 50), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255))



def draw_face_roll( img, leye, reye, good=False ):

    color_A = (255, 0, 50) if not good else (0, 255, 0)
    color_B = (50, 0, 255) if not good else (0, 255, 0)

    cv.line( img,
        (int(leye.x),  int(leye.y)),
        (int(reye.x),  int(leye.y)),
        color_A, thickness=5
    )

    cv.line( img,
        (int(reye.x),  int(reye.y)),
        (int(leye.x),  int(reye.y)),
        color_B, thickness=5
    )



def draw_face_yaw( img, leye, philtrum, reye, good=False ):

    color_A = (255, 0, 50) if not good else (0, 255, 0)
    color_B = (50, 0, 255) if not good else (0, 255, 0)


    # left eye <---> midface
    # -------------------------------------------------------
    cv.line( img,
        (int(leye.x),      int(philtrum.y)),
        (int(philtrum.x),  int(philtrum.y)),
        color_A, thickness=5
    )

    cv.line( img,
        (int(leye.x),  int(leye.y)),
        (int(leye.x),  int(philtrum.y)),
        color_B, thickness=5
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
        color_B, thickness=5
    )

    cv.line( img,
        (int(reye.x),  int(reye.y)),
        (int(reye.x),  int(philtrum.y)),
        color_A, thickness=5
    )

    cv.line( img,
        (int(reye.x),  int(reye.y)),
        (int(philtrum.x),  int(philtrum.y)),
        (0, 0, 0), thickness=1
    )
    # -------------------------------------------------------



def evaluate_face_roll( img, leye, reye, draw=False ) -> tuple[bool, float]:

    # leye.y should rougly equal reye.y for roll alignment

    EPSILON = 5

    roll_fitness = math.fabs(leye.y - reye.y)
    roll_good  = -EPSILON <= roll_fitness <= +EPSILON

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
    yaw_good    = yaw_fitness >= 1 - EPSILON

    print(yaw_fitness)

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
        color_A, thickness=5
    )

    cv.line( img,
        (int(lm0.x),   int(lm0.y)),
        (int(lm0.x),   int(lm17.y)),
        color_B, thickness=5
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

    real_depth = float(input("Real hand depth (mm): "))
    real_0_17 = float(input("Real distance between hand landmarks 0 and 17 (mm): "))

    handDetector = HandDetector()
    faceDetector = FaceDetector()

    cap = cv.VideoCapture(0)
    cap.set(cv.CAP_PROP_FRAME_WIDTH,  1280)
    cap.set(cv.CAP_PROP_FRAME_HEIGHT, 720)

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


        if not (h_roll_good is None or f_roll_good is None or f_yaw_good is None):
            if h_roll_good and f_roll_good and f_yaw_good:
                hfRatio.updatePixelDistances(img, handDetector, faceDetector)


        cv.imshow("Image", img)
        if cv.waitKey(1) == 27:
            break

    hfRatio.writeINI("test.ini")


main()

