from .renderer import *


PRIMITIVE_UVSPHERE = 0
PRIMITIVE_CYLINDER = 1
PRIMITIVE_CUBE     = 2


__primitives = [ None, None, None ]



def loadPrimitive( enum_name, objpath: str ):
    __primitives[enum_name] = loadOBJ(objpath)



def getPrimitive( enum_name ) -> ModelHandle:
    return __primitives[enum_name]

