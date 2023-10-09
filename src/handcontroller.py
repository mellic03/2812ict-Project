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


    def update( self, hr: HandRenderer, cam: idk.Camera, dtime: float ) -> None:

        self.grabbing = methods.hand_is_grabbing(hr.wlms)

        self.velocity = glm.clamp(0.9*self.velocity, -0.2, +0.2)

        if self.grabbing:
            delta = glm.vec3(hr.center_raw) - glm.vec3(hr.center_raw_prev)
            self.velocity += glm.length(delta) * glm.vec3(0, 0, glm.sign(delta.z))
            cam.translate(self.velocity, scale=glm.vec3(1, 0, 1))

