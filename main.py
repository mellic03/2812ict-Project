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


    monkey = Model()
    monkey_h = monkey.loadOBJ(b"models/cube/", b"dog.obj", b"cube.mtl", b"container.png")

    cube = Model()
    cube_h = cube.loadOBJ(b"models/cube/", b"cube.obj", b"cube.mtl", b"container.png")


    basic_shader: GLuint = ren.compileShaderProgram("./", "basic.vs", "basic.fs")
    tex_shader: GLuint = ren.compileShaderProgram("./", "textured.vs", "textured.fs")

    trans1 = glm.translate(glm.mat4(1.0), glm.vec3( 2.0, 0.0, -4.0))
    trans1 = glm.scale(trans1, glm.vec3(0.8, 0.8, 0.8))
    trans2 = glm.translate(glm.mat4(1.0), glm.vec3(-2.0, 0.0, -4.0))


    theta = 0
    while (ren.running()):
        ren.beginFrame()

        rot = glm.rotate(3.1415, glm.vec3(0.0, 0.0, 1.0))
        rot = glm.rotate(theta, glm.vec3(0.0, 1.0, 0.0)) * rot

        glUseProgram(basic_shader)
        ren.setmat4(basic_shader, "proj", proj)
        ren.setmat4(basic_shader, "model", trans2*rot)
        ren.drawVertices(monkey_h)

        glUseProgram(tex_shader)
        ren.setmat4(tex_shader, "proj", proj)
        ren.setmat4(tex_shader, "model", trans1*rot)
        ren.drawVerticesTextured(tex_shader, cube_h)


        theta += 0.01
        ren.endFrame()


if __name__ == "__main__":
    main()

