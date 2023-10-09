import glm
import idk
import methods
from handrenderer import HandRenderer



class HandController:

    def __init__( self ) -> None:

        self.grabbing = False
        self.velocity = glm.vec3(0)
        self.finger_states = [ False ] * 5


    def update( self, hr: HandRenderer, cam: idk.Camera ) -> None:
        
        self.grabbing = methods.hand_is_grabbing(hr.wlms)

        self.velocity = glm.clamp(0.9*self.velocity, -0.1, +0.1)


        if self.grabbing:
            delta = glm.vec3(hr.wlms[0]) - glm.vec3(hr.wlms_prev[0])
            self.velocity += delta


        cam.translate(self.velocity)



