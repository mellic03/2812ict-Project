# OpenGL -------------------------------------------
# This program requires a python wrapper for OpenGL
# along with SDL2, numpy and ctypes.
# pip install ctypes numpy pysdl2 PyOpenGL PyOpenGL_accelerate
# --------------------------------------------------
from renderer import Renderer
from renderer import Model
from OpenGL.GL import *
import glm as glm


VERTICES = [
#    x     y     z     u     v
   -0.7, -0.9,  0.0,  #0.0,   0.0,
    0.9, -0.9,  0.0,  #1.0,   0.0,
    0.9,  0.7,  0.0,  #1.0,   1.0,

   -0.9,  0.9,  0.0,  #0.0,   0.0,
   -0.9, -0.7,  0.0,  #1.0,   0.0,
    0.7,  0.9,  0.0,  #1.0,   1.0
]


def main():
    width = 1000
    height = 1000
    ren = Renderer(b"OpenGL Renderer Python", width, height)
    proj = glm.perspective(80.0, 1, 1, 100)

    cube = Model()
    cube.loadOBJ("models/cube/", "dog.obj", "cube.mtl", "container.png")

    basic_shader: GLuint = ren.compileShaderProgram("./", "basic.vs", "basic.fs")
    VAO, VBO = ren.loadVertices(cube.glVertices)

    glUseProgram(basic_shader)
    theta = 0

    while (ren.running()):
        ren.beginFrame()

        trans = glm.translate(glm.mat4(1.0), glm.vec3(0.0, 0.0, -3.0))

        rot = glm.rotate(3.1415, glm.vec3(0.0, 0.0, 1.0))
        rot = glm.rotate(theta, glm.vec3(0.0, 1.0, 0.0)) * rot
        ren.setmat4(basic_shader, "proj", proj)
        ren.setmat4(basic_shader, "model", trans*rot)
        ren.drawVertices(VAO, cube.glVertices)

        theta += 0.01

        ren.endFrame()


if __name__ == "__main__":
    main()

