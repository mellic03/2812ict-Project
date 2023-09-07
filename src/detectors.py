import cv2 as cv
import mediapipe as mp


class FaceDetector:
    def __init__(self) -> None:

        self.face_mesh = mp.solutions.face_mesh
        self.mpFace  = mp.solutions.face_mesh.FaceMesh()
        self.mpDraw  = mp.solutions.drawing_utils
        self.drawStyles  = mp.solutions.drawing_styles
        self.m_results = None
        self.img = None


    def detect(self, img) -> None:
        self.img = img
        imgRGB = cv.cvtColor(self.img, cv.COLOR_BGR2RGB)
        self.m_results = self.mpFace.process(imgRGB)


    def draw(self) -> None:
        if self.m_results and self.m_results.multi_face_landmarks:
            for handLms in self.m_results.multi_face_landmarks:
                self.mpDraw.draw_landmarks(
                image=self.img,
                landmark_list=handLms,
                connections=self.face_mesh.FACEMESH_TESSELATION,
                landmark_drawing_spec=None,
                connection_drawing_spec=self.drawStyles
                .get_default_face_mesh_tesselation_style()
          )
        cv.namedWindow("win0")
        cv.imshow("Image0", self.img)
        cv.waitKey(2)


    def results(self):
        return self.m_results




class HandDetector:
    def __init__(self) -> None:
        self.hands = mp.solutions.hands
        self.mpHands  = mp.solutions.hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.9,
            min_tracking_confidence=0.9
        )
        self.mpDraw  = mp.solutions.drawing_utils
        self.drawStyles  = mp.solutions.drawing_styles
        self.m_results = None
        self.img = None

    
    def detect(self, img) -> None:
        self.img = img
        imgRGB = cv.cvtColor(self.img, cv.COLOR_BGR2RGB)
        self.m_results = self.mpHands.process(imgRGB)


    def draw(self) -> None:
        if self.m_results and self.m_results.multi_hand_landmarks:
            for handLms in self.m_results.multi_hand_landmarks:
                self.mpDraw.draw_landmarks(
                    self.img,
                    handLms,
                    self.hands.HAND_CONNECTIONS
                )
        cv.imshow("Image", self.img)
        cv.waitKey(1)


    def results(self):
        return self.m_results

