# OpenGL -------------------------------------------
# This program requires a python wrapper for OpenGL
# along with SDL2, numpy and ctypes.
# pip install ctypes numpy pysdl2 PyOpenGL PyOpenGL_accelerate
# --------------------------------------------------
from renderer import Renderer
from renderer import Model
from OpenGL.GL import *
import glm as glm


def main():
    width = 1000
    height = 1000
    ren = Renderer(b"OpenGL Renderer Python", width, height)
    proj = glm.perspective(80.0, width/height, 1, 100)

    cube = Model()
    model_handle = cube.loadOBJ(b"models/cube/", b"cube.obj", b"cube.mtl", b"container.png")

    basic_shader: GLuint = ren.compileShaderProgram("./", "basic.vs", "basic.fs")
    glUseProgram(basic_shader)

    tex_shader: GLuint = ren.compileShaderProgram("./", "textured.vs", "textured.fs")
    glUseProgram(tex_shader)


    theta = 0
    while (ren.running()):
        ren.beginFrame()


        trans = glm.translate(glm.mat4(1.0), glm.vec3(0.0, 0.0, -3.0))
        rot = glm.rotate(3.1415, glm.vec3(0.0, 0.0, 1.0))
        rot = glm.rotate(theta, glm.vec3(0.0, 1.0, 0.0)) * rot
        ren.setmat4(tex_shader, "proj", proj)
        ren.setmat4(tex_shader, "model", trans*rot)

        # ren.drawVertices(model_handle)
        ren.drawVerticesTextured(tex_shader, model_handle)


        theta += 0.01
        ren.endFrame()


if __name__ == "__main__":
    main()

