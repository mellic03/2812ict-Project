from sdl2 import *
from sdl2.sdlimage import *
import sdl2.ext
import ctypes
from OpenGL.GL import *
from OpenGL.GL import shaders
import numpy as np
import glm as glm
from .camera import *





"""
    Not much to see here, just a bunch of poorly ported C++ code.
"""




VERTEX_NUM_ELEMENTS = 8
SIZEOF_FLOAT = sizeof(ctypes.c_float)
SIZEOF_VERTEX = VERTEX_NUM_ELEMENTS*SIZEOF_FLOAT



idk__programs = { }

def storeProgram( name: str, shader_id: GLuint ) -> None:
    idk__programs[name] = shader_id


def getProgram( name ) -> GLuint:
    return idk__programs[name]




class ModelHandle:
    def __init__(self, VAO, VBO, num_elements, glTextureID) -> None:
        self.VAO = VAO
        self.VBO = VBO
        self.num_elements = num_elements
        self.glTextureID  = glTextureID


def __obj_extractFaceIndices(abc: str):
    arr = abc.split("/")
    return [int(arr[0])-1, int(arr[1])-1, int(arr[2])-1]


def __load_obj(filepath):
    vertices = []
    fh = open(filepath, "r")
    positions = []
    normals   = []
    uvs       = []

    for line in fh:
        tokens = line.strip("\n").split(" ")

        if tokens[0] == "v":
            positions.append([
                float(tokens[1]),
                float(tokens[2]),
                float(tokens[3])
            ])

        elif tokens[0] == "vn":
            normals.append([
                float(tokens[1]),
                float(tokens[2]),
                float(tokens[3])
            ])

        elif tokens[0] == "vt":
            uvs.append([
                float(tokens[1]),
                1.0-float(tokens[2])
            ])

        elif tokens[0] == "f":
            i1 = __obj_extractFaceIndices(tokens[1])
            i2 = __obj_extractFaceIndices(tokens[2])
            i3 = __obj_extractFaceIndices(tokens[3])

            vertices += positions[i1[0]]
            vertices += normals  [i1[2]]
            vertices += uvs      [i1[1]]

            vertices += positions[i2[0]]
            vertices += normals  [i2[2]]
            vertices += uvs      [i2[1]]

            vertices += positions[i3[0]]
            vertices += normals  [i3[2]]
            vertices += uvs      [i3[1]]

    return vertices



def __loadVertices(vertices: list[float], usage=GL_STATIC_DRAW):
    NPVERTS = np.array(vertices, dtype=np.float32)
    
    VAO = glGenVertexArrays(1)
    VBO = glGenBuffers(1)

    glBindVertexArray(VAO)
    glBindBuffer(GL_ARRAY_BUFFER, VBO)
    glBufferData(GL_ARRAY_BUFFER, NPVERTS.nbytes, NPVERTS, usage)    

    # Position attribute
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 8*SIZEOF_FLOAT, ctypes.c_void_p(0*SIZEOF_FLOAT))
    glEnableVertexAttribArray(0)

    # Normal attribute
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 8*SIZEOF_FLOAT, ctypes.c_void_p(3*SIZEOF_FLOAT))
    glEnableVertexAttribArray(1)

    # Texture coordinate attribute
    glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, 8*SIZEOF_FLOAT, ctypes.c_void_p(6*SIZEOF_FLOAT))
    glEnableVertexAttribArray(2)

    glBindBuffer(GL_ARRAY_BUFFER, 0)
    glBindVertexArray(0)

    return (VAO, VBO)



def loadVertices(vertices: list[float], usage=GL_STATIC_DRAW):
    VAO, VBO = __loadVertices(vertices, usage)
    return ModelHandle(
        VAO, VBO,
        len(vertices) // VERTEX_NUM_ELEMENTS,
        0
    )


# Load an image texture from file and return an identifying GLuint ID
def __loadTexture(filepath):
    img: SDL_Surface = IMG_Load(filepath)
    u32_img = ctypes.cast(img[0].pixels, ctypes.POINTER(ctypes.c_uint32))

    texture_id = glGenTextures(1)        
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glPixelStorei(GL_UNPACK_ALIGNMENT, 1)

    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, img[0].w, img[0].h, 0, GL_RGBA, GL_UNSIGNED_BYTE, u32_img)

    glGenerateMipmap(GL_TEXTURE_2D)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    glBindTexture(GL_TEXTURE_2D, 0)

    return texture_id



def loadOBJ(obj, texture=None, usage=GL_STATIC_DRAW) -> ModelHandle:
    vertices = __load_obj(obj)
    VAO, VBO = __loadVertices(vertices, usage)

    glTextureID = 0
    if texture != None:
        glTextureID = __loadTexture(texture)

    return ModelHandle(
        VAO, VBO,
        len(vertices) // VERTEX_NUM_ELEMENTS,
        glTextureID
    )



class Renderer:

    __width  = 0
    __height = 0
    __name   = ""

    __running = True
    __SDL_window = SDL_Window
    __SDL_gl_context = SDL_GLContext


    def ren_init(self) -> None:
        SDL_Init(SDL_INIT_VIDEO)

        self.__SDL_window = SDL_CreateWindow(
            self.__name,
            SDL_WINDOWPOS_CENTERED,
            SDL_WINDOWPOS_CENTERED,
            self.__width,
            self.__height,
            SDL_WINDOW_OPENGL | SDL_WINDOW_RESIZABLE | SDL_WINDOW_MAXIMIZED
        )

        SDL_GL_SetAttribute(SDL_GL_CONTEXT_MAJOR_VERSION, 3)
        SDL_GL_SetAttribute(SDL_GL_CONTEXT_MINOR_VERSION, 3)
        self.__SDL_gl_context = SDL_GL_CreateContext(self.__SDL_window)
        SDL_GL_MakeCurrent(self.__SDL_window, self.__SDL_gl_context)

        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)


    def __init__(self, name, width, height, startGL = False) -> None:
        self.__width  = width
        self.__height = height
        self.__name   = name
        if startGL:
            self.ren_init()


    def running(self) -> bool:
        return self.__running

    def width(self) -> int:
        return self.__width

    def height(self) -> int:
        return self.__height
    
    def windowSize(self) -> tuple[int, int]:
        return (self.__width, self.__height)


    def beginFrame(self, cam: Camera) -> None:
        glViewport(0, 0, self.__width, self.__height)
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        glClearColor(0.0, 0.0, 0.0, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        for event in sdl2.ext.get_events():
            if event.type == SDL_WINDOWEVENT:
                if event.window.event == SDL_WINDOWEVENT_CLOSE:
                    self.__running = False
                elif event.window.event == SDL_WINDOWEVENT_SIZE_CHANGED:
                    self.__width = event.window.data1
                    self.__height = event.window.data2

                    cam.setProjection(cam.fov(), self.__width, self.__height)


        for key in idk__programs:
            shader_id = idk__programs[key]
            glUseProgram(shader_id)
            setmat4(shader_id, "un_proj", cam.projection())
            setmat4(shader_id, "un_view", cam.viewMatrix())


        SDL_PumpEvents()


    def endFrame(self) -> None:
        SDL_GL_SwapWindow(self.__SDL_window)





def setint(shader_id, name, value):
    uniform_loc = glGetUniformLocation(shader_id, name)
    glUniform1i(uniform_loc, value)

def setfloat(shader_id, name, value):
    uniform_loc = glGetUniformLocation(shader_id, name)
    glUniform1f(uniform_loc, value)

def setvec3(shader_id, name, vec: glm.vec3):
    uniform_loc = glGetUniformLocation(shader_id, name)
    glUniform3f(uniform_loc, vec.x, vec.y, vec.z)

def setmat4(shader_id, name, mat: glm.mat4):
    uniform_loc = glGetUniformLocation(shader_id, name)
    glUniformMatrix4fv(uniform_loc, 1, GL_FALSE, glm.value_ptr(mat))



# Load an image texture from file and return an identifying GLuint ID
def loadTexture(filepath):
    img: SDL_Surface = IMG_Load(filepath)
    u32_img = ctypes.cast(img[0].pixels, ctypes.POINTER(ctypes.c_uint32))

    texture_id = glGenTextures(1)        
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glPixelStorei(GL_UNPACK_ALIGNMENT, 1)

    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, img[0].w, img[0].h, 0, GL_RGBA, GL_UNSIGNED_BYTE, u32_img)

    glGenerateMipmap(GL_TEXTURE_2D)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    glBindTexture(GL_TEXTURE_2D, 0)

    return texture_id



# Compile a vertex and fragment shader and return an identifying GLuint ID
def compileShaderProgram(root: str, vert: str, frag: str) -> GLuint:
    vert_src: str
    frag_src: str
    
    with open(root + vert, "r") as file:
        vert_src = file.read()
    with open(root + frag, "r") as file:
        frag_src = file.read()
    
    vert_id = shaders.compileShader(vert_src, GL_VERTEX_SHADER)
    frag_id = shaders.compileShader(frag_src, GL_FRAGMENT_SHADER)
    shader_id = glCreateProgram()
    glAttachShader(shader_id, vert_id)
    glAttachShader(shader_id, frag_id)
    
    glLinkProgram(shader_id)
    if glGetProgramiv(shader_id, GL_LINK_STATUS) != GL_TRUE:
        sys.stderr.write("Error: {0}\n".format(glGetProgramInfoLog(shader_id)))
        exit(4)

    glDeleteShader(vert_id)
    glDeleteShader(frag_id)

    return shader_id



def loadVertices(vertices: list[float], usage=GL_STATIC_DRAW):
    NPVERTS = np.array(vertices, dtype=np.float32)
    
    VAO = glGenVertexArrays(1)
    VBO = glGenBuffers(1)

    glBindVertexArray(VAO)
    glBindBuffer(GL_ARRAY_BUFFER, VBO)
    glBufferData(GL_ARRAY_BUFFER, NPVERTS.nbytes, NPVERTS, usage)    

    # Position attribute
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 8*SIZEOF_FLOAT, ctypes.c_void_p(0*SIZEOF_FLOAT))
    glEnableVertexAttribArray(0)

    # Normal attribute
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 8*SIZEOF_FLOAT, ctypes.c_void_p(3*SIZEOF_FLOAT))
    glEnableVertexAttribArray(1)

    # Texture coordinate attribute
    glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, 8*SIZEOF_FLOAT, ctypes.c_void_p(6*SIZEOF_FLOAT))
    glEnableVertexAttribArray(2)

    glBindVertexArray(0)

    return ModelHandle(
        VAO, VBO,
        len(vertices) // VERTEX_NUM_ELEMENTS,
        0
    )



def setint(shader_id, name, value):
    uniform_loc = glGetUniformLocation(shader_id, name)
    glUniform1i(uniform_loc, value)


def loadVerticesIndexed(vertices: np.ndarray, indices: np.ndarray, usage=GL_STATIC_DRAW):
    NP_VERTICES = vertices
    NP_INDICES  = indices
    
    VAO = glGenVertexArrays(1)
    VBO = glGenBuffers(1)
    IBO = glGenBuffers(1)

    glBindVertexArray(VAO)

    glBindBuffer(GL_ARRAY_BUFFER, VBO)
    glBufferData(GL_ARRAY_BUFFER, NP_VERTICES.nbytes, NP_VERTICES, usage)    

    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, IBO)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, NP_INDICES.nbytes, NP_INDICES, GL_STATIC_DRAW)    

    # Position attribute
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 8*SIZEOF_FLOAT, ctypes.c_void_p(0*SIZEOF_FLOAT))
    glEnableVertexAttribArray(0)

    # Normal attribute
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 8*SIZEOF_FLOAT, ctypes.c_void_p(3*SIZEOF_FLOAT))
    glEnableVertexAttribArray(1)

    # Texture coordinate attribute
    glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, 8*SIZEOF_FLOAT, ctypes.c_void_p(6*SIZEOF_FLOAT))
    glEnableVertexAttribArray(2)

    glBindVertexArray(0)

    return ModelHandle(
        VAO, VBO,
        len(indices),
        0
    )


def subData( mh, vertices: np.ndarray ):
    glBindVertexArray(mh.VAO)
    glBindBuffer(GL_ARRAY_BUFFER, mh.VBO)
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_DYNAMIC_DRAW)
    glBindVertexArray(0)


def indexedSubData( VAO, VBO, vertices: np.ndarray ):
    glBindVertexArray(VAO)
    glBindBuffer(GL_ARRAY_BUFFER, VBO)
    glBufferSubData(GL_ARRAY_BUFFER, 0, vertices.nbytes, vertices)
    glBindVertexArray(0)


def drawVertices(mh: ModelHandle, gl_mode=GL_TRIANGLES) -> None:
    glBindVertexArray(mh.VAO)
    glDrawArrays(gl_mode, 0, mh.num_elements)
    glBindVertexArray(0)


def drawVerticesTextured(shader_id, mh: ModelHandle) -> None:
    glBindVertexArray(mh.VAO)
    glActiveTexture(GL_TEXTURE0)
    glBindTexture(GL_TEXTURE_2D, mh.glTextureID)
    setint(shader_id, "un_texture", 0)
    glDrawArrays(GL_TRIANGLES, 0, mh.num_elements)
    glBindVertexArray(0)


def drawVerticesIndexed(mh: ModelHandle, gl_mode=GL_TRIANGLES) -> None:
    glBindVertexArray(mh.VAO)
    glDrawElements(gl_mode, mh.num_elements, GL_UNSIGNED_INT, ctypes.c_void_p(0))
    glBindVertexArray(0)


def setTexture( shader_id, texture_unit, glTextureID, name ):
    glActiveTexture(GL_TEXTURE0 + texture_unit)
    glBindTexture(GL_TEXTURE_2D, glTextureID)
    setint(shader_id, name, texture_unit)



def drawVerticesIndexedTextured(mh: ModelHandle, shader_id, gl_mode=GL_TRIANGLES) -> None:
    glBindVertexArray(mh.VAO)
    glActiveTexture(GL_TEXTURE0)
    glBindTexture(GL_TEXTURE_2D, mh.glTextureID)
    setint(shader_id, "un_texture", 0)
    glDrawElements(gl_mode, mh.num_elements, GL_UNSIGNED_INT, ctypes.c_void_p(0))
    glBindVertexArray(0)

