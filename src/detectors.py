import cv2 as cv
import mediapipe as mp

import math

class FaceDetector:
    def __init__(self) -> None:

        self.face_mesh   = mp.solutions.face_mesh
        self.mpFace      = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True, max_num_faces=1)
        self.mpDraw      = mp.solutions.drawing_utils
        self.drawStyles  = mp.solutions.drawing_styles
        self.m_results   = None


    def detect(self, img) -> None:
        imgRGB = cv.cvtColor(img, cv.COLOR_BGR2RGB)
        self.m_results = self.mpFace.process(imgRGB)


    def __draw_debug(self, img, real_depth, real_a):
        
        return


    def draw(self, img, debug=None) -> None:

        if debug == True:
            return img

        if self.m_results and self.m_results.multi_face_landmarks:
            for handLms in self.m_results.multi_face_landmarks:
                self.mpDraw.draw_landmarks(
                image=img,
                landmark_list=handLms,
                connections=self.face_mesh.FACEMESH_LEFT_IRIS,
                landmark_drawing_spec=None,
                connection_drawing_spec=self.drawStyles
                .get_default_face_mesh_tesselation_style()
            )
            for handLms in self.m_results.multi_face_landmarks:
                self.mpDraw.draw_landmarks(
                image=img,
                landmark_list=handLms,
                connections=self.face_mesh.FACEMESH_RIGHT_IRIS,
                landmark_drawing_spec=None,
                connection_drawing_spec=self.drawStyles
                .get_default_face_mesh_tesselation_style()
            )
        return img

    def results(self):
        return self.m_results





class HandDetector:
    def __init__(self) -> None:
        self.hands = mp.solutions.hands
        self.mpHands  = mp.solutions.hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.2,
            min_tracking_confidence=0.2
        )
        self.mpDraw  = mp.solutions.drawing_utils
        self.drawStyles  = mp.solutions.drawing_styles
        self.m_results = None
        self.grabbing = False


    def detect(self, img) -> None:
        imgRGB = cv.cvtColor(img, cv.COLOR_BGR2RGB)
        self.m_results = self.mpHands.process(imgRGB)


    def __draw_debug(self, img, real_depth_mm: float, real_5_17: float) -> None:

        if self.m_results and self.m_results.multi_hand_landmarks:
            for handLms in self.m_results.multi_hand_landmarks:
                self.mpDraw.draw_landmarks(
                    img,
                    handLms,
                    self.hands.HAND_CONNECTIONS
                )
                
                x5  = int( img.shape[1] * handLms.landmark[5].x)
                x17 = int( img.shape[1] * handLms.landmark[17].x)
                y5  = int( img.shape[0] * handLms.landmark[5].y)
                y17 = int( img.shape[0] * handLms.landmark[17].y)

                color = (0, 0, 255)
                if math.fabs(y5-y17) < 5.0:
                    color = (0, 255, 0)

                cv.line(img, (0, y5), (img.shape[1], y5), color, thickness=5)
                cv.line(img, (0, y17), (img.shape[1], y17), color, thickness=5)
                
                pixel_5_17 = math.fabs(x5 - x17)

                focal_length = (real_depth_mm * pixel_5_17) / real_5_17

                cv.putText(img, "f: %.2f" % (focal_length), (10, 50), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255))



    def draw(self, img, debug=False, real_depth=None, real_0_5_mm=None) -> None:

        if debug == True:
            self.__draw_debug(img, real_depth, real_0_5_mm)
            return img

        if self.m_results and self.m_results.multi_hand_landmarks:
            for handLms in self.m_results.multi_hand_landmarks:
                self.mpDraw.draw_landmarks(
                    img,
                    handLms,
                    self.hands.HAND_CONNECTIONS
                )

                if self.grabbing == False:
                    continue

                for lms in handLms.landmark:
                    cv.circle(img, (int(img.shape[1]*lms.x), int(img.shape[0]*lms.y)), 5, (0, 255, 0), cv.FILLED)

        return img


    def results(self):
        return self.m_results

