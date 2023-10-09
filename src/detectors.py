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
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.mpDraw  = mp.solutions.drawing_utils
        self.drawStyles  = mp.solutions.drawing_styles
        self.m_results = None
        self.grabbing = False


    def detect(self, img) -> None:
        imgRGB = cv.cvtColor(img, cv.COLOR_BGR2RGB)
        self.m_results = self.mpHands.process(imgRGB)


    def draw(self, img) -> None:

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

