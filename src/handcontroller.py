import math
import glm
import numpy as np
import idk
import methods
from handrenderer import HandRenderer



class HandController:

    def __init__( self ) -> None:

        self.grabbing = False
        self.velocity = glm.vec3(0)
        self.finger_states = [ False ] * 5


    def update( self, hr: HandRenderer, cam: idk.Camera, dtime: float ) -> None:

        self.grabbing = methods.hand_is_grabbing(hr.wlms)
        self.velocity *= 0.9

        if self.grabbing:
            delta = glm.vec3(hr.center_raw) - glm.vec3(hr.center_raw_prev)
            self.velocity += glm.length(delta) * glm.sign(delta.z) * glm.vec3(0, 0, 1)


            cam.translate(self.velocity, scale=glm.vec3(1, 0, 1))



