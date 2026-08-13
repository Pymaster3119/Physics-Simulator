import pygame as pg
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import numpy as np
import math
import readspheres
import re
import tkinter


SCREEN_SIZE = (500, 500)

WINDOW_CREATION_FLAGS = pg.OPENGL | pg.DOUBLEBUF
FRAMERATE = 30
DATA_TYPE_COLORED_VERTEX = np.dtype({
    'names': ['x','y','z'],
    'formats': [np.float32, np.float32, np.float32],
    'offsets': [0, 4, 8],
    'itemsize': 12})

CAMERAPOSITION = [0,0,-3]
CAMERAROTATION = [0,0,0]
FORCE = [0,0,0]
MAX_FORCE = 2.7e6
LIGHTSPEED = 299792458
CAMERAVELOCITY = [0,0,0]

pg.init()
pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 3)
pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 3)
pg.display.gl_set_attribute(pg.GL_CONTEXT_PROFILE_MASK, pg.GL_CONTEXT_PROFILE_CORE)
screen = pg.display.set_mode(SCREEN_SIZE, WINDOW_CREATION_FLAGS)
clock = pg.time.Clock()

def make_shader(vert, frag):
    vert_mod = make_shader_module(vert, GL_VERTEX_SHADER)
    frag_mod = make_shader_module(frag, GL_FRAGMENT_SHADER)
    return compileProgram(vert_mod, frag_mod)

def make_shader_module (filename, module_type):
    with open(filename, "r") as x:
        source = x.readlines()
        return compileShader(source, module_type)

def make_compute_shader(filename):
    comp_mod = make_shader_module(filename, GL_COMPUTE_SHADER)
    return compileProgram(comp_mod)

class Mesh:
    def __init__(self):
        self.VAO = glGenVertexArrays(1)
        self.VBO = glGenBuffers(1)
        self.vertex_count = 0
    def build_colored_triangle(self):
        vertices = np.zeros(3, dtype=DATA_TYPE_COLORED_VERTEX)

        glBindVertexArray(self.VAO)
        glBindBuffer(GL_ARRAY_BUFFER, self.VBO)
        atttribute_index = 0
        size = 3
        offset = 0
        stride = DATA_TYPE_COLORED_VERTEX.itemsize
        glVertexAttribPointer(atttribute_index, size, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(offset))
        glEnableVertexAttribArray(atttribute_index)

        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)
        return self
    def draw(self):
        glBindVertexArray(self.VAO)
        glDrawArrays(GL_TRIANGLES, 0, 6)
    def destroy(self):
        glDeleteVertexArrays(1, (self.VAO,))
        glDeleteBuffers(1, (self.VBO,))

class Renderer:
    SCREEN_COLOR = [0,0,0,1]
    def __init__(self):
        glClearColor(*self.SCREEN_COLOR)
        self.mesh = Mesh().build_colored_triangle()
        self.shader = make_shader("vertex.txt", "fragment.txt")
        self.widthloc = glGetUniformLocation(self.shader, "u_screenWidth")
        self.heightloc = glGetUniformLocation(self.shader, "u_screenHeight")
        self.cameraPosLoc = glGetUniformLocation(self.shader, "u_cameraPos")
        self.cameraAngleLoc = glGetUniformLocation(self.shader, "u_cameraAngle")
        self.matrixLoc = glGetUniformLocation(self.shader, "u_rotation_matrix")
        self.point_count_loc = glGetUniformLocation(self.shader, "u_pointCount")
        self.point_buffer_loc = glGetUniformLocation(self.shader, "u_points_tex")
        self.camearmass, self.cameravelocity, self.cameraforce = readspheres.read_cam()
        self.points = readspheres.get_full_points()
        match = re.match(r"^\(([^,]+),([^,]+),([^,]+)\)$", self.cameravelocity)
        self.dT = (1/FRAMERATE)
        self.referenceFrameDT = (1/FRAMERATE)
        if match:
            vx, vy, vz = match.groups()
            vx = float(vx)
            vy = float(vy)
            vz = float(vz)
            self.cameravelocity = [vx, vy, vz]
        else:
            raise Exception("One of the velocity strings is not correct: " + self.cameravelocity)


    def update_point(self, point):
        x,y,z,r,mass,velocity, force_controlled_by_keyboard = point
        velocity = velocity.strip()
        match = re.match(r"^\(([^,]+),([^,]+),([^,]+)\)$", velocity)
        if match:
            vx, vy, vz = match.groups()
            v = np.linalg.norm(np.array([vx,vy,vz]))
            dt = self.referenceFrameDT * math.sqrt(1 - ((v**2)/(LIGHTSPEED**2)))
            x += dt * float(vx)
            y += dt * float(vy)
            z += dt * float(vz)
        else:
            raise Exception("One of the velocity strings is not correct: " + velocity)
        return [x,y,z,r,mass,velocity, force_controlled_by_keyboard]
    def update_points(self):
        global CAMERAPOSITION, CAMERAVELOCITY
        # CALCULATE WORLD DELTATIME
        v = np.linalg.norm(np.array(CAMERAVELOCITY))
        gamma = 1/ math.sqrt(1 - (v/LIGHTSPEED) ** 2)
        self.referenceFrameDT = self.dT * gamma

        new_points = []
        for i in self.points:
            new_points.append(self.update_point(i))
        self.points = new_points
        cx, cy, cz = CAMERAPOSITION
        vx, vy, vz = self.cameravelocity
        if self.cameraforce:
            #USING: A = F/m
            ax = FORCE[0] / self.camearmass
            ay = FORCE[1] / self.camearmass
            az = FORCE[2] / self.camearmass

            vx += self.dT * float(ax)
            vy += self.dT * float(ay)
            vz += self.dT * float(az)
            
        cx += self.dT * float(vx)
        cy += self.dT * float(vy)
        cz += self.dT * float(vz)
        CAMERAPOSITION = (cx, cy, cz)
        self.cameravelocity = [vx, vy, vz]
        CAMERAVELOCITY = self.cameravelocity
        
    def write_to_json(self):
        with open("simulatorstats.json", "w") as txt:
            readspheres.json.dump({"CAMERAVELOCITY": CAMERAVELOCITY, "LIGHTSPEED": LIGHTSPEED, "DELTATIME": self.referenceFrameDT, "FRAMERATE": FRAMERATE}, txt)

    def draw(self):
        print("Frame passed!")
        self.update_points()
        matx = np.array([
            [1.0, 0.0, 0.0],
            [0.0, math.cos(math.radians(CAMERAROTATION[0])), -math.sin(math.radians(CAMERAROTATION[0]))],
            [0.0, math.sin(math.radians(CAMERAROTATION[0])),  math.cos(math.radians(CAMERAROTATION[0]))],
        ], dtype=np.float32)

        maty = np.array([
            [math.cos(math.radians(CAMERAROTATION[1])),  0.0, math.sin(math.radians(CAMERAROTATION[1]))],
            [0.0, 1.0, 0.0],
            [-math.sin(math.radians(CAMERAROTATION[1])), 0.0, math.cos(math.radians(CAMERAROTATION[1]))]
        ], dtype=np.float32)

        matz = np.array([
            [math.cos(math.radians(CAMERAROTATION[2])), -math.sin(math.radians(CAMERAROTATION[2])), 0.0],
            [math.sin(math.radians(CAMERAROTATION[2])), math.cos(math.radians(CAMERAROTATION[2])) , 0.0],
            [0.0, 0.0, 1.0]
        ], dtype=np.float32)
        rotmat = matz @ maty @ matx

        
        N = len(self.points)
        points = [i[0:4] for i in self.points]
        data = np.array(points, dtype=np.float64)
        data = data / 1e12
        data = data.astype(np.float32)
        buf = glGenBuffers(1)
        glBindBuffer(GL_TEXTURE_BUFFER, buf)
        glBufferData(GL_TEXTURE_BUFFER, data.nbytes, data, GL_STATIC_DRAW)
        tex = glGenTextures(1)
        glBindTexture(GL_TEXTURE_BUFFER, tex)
        glTexBuffer(GL_TEXTURE_BUFFER, GL_RGBA32F, buf)
        texture_unit = 0
        glActiveTexture(GL_TEXTURE0 + texture_unit)
        glBindTexture(GL_TEXTURE_BUFFER, tex)

        glClear(GL_COLOR_BUFFER_BIT)
        glUseProgram(self.shader)

        # Now that the program is active, set sampler and other uniforms
        glUniform1i(self.point_buffer_loc, texture_unit)
        glUniform1i(self.point_count_loc, N)
        glUniform1f(self.widthloc, SCREEN_SIZE[0])
        glUniform1f(self.heightloc, SCREEN_SIZE[1])
        glUniform3fv(self.cameraPosLoc, 1, np.array(CAMERAPOSITION) / 1e+12)
        glUniform3fv(self.cameraAngleLoc, 1, CAMERAROTATION)
        glUniformMatrix3fv(self.matrixLoc, 1, False, rotmat)
        self.mesh.draw()
        self.write_to_json()

    def destroy(self):
        self.mesh.destroy()
        glDeleteProgram(self.shader)

running = True
r = Renderer()
while running:
    for i in pg.event.get():
        if i.type == pg.QUIT:
            running = False
    keys = pg.key.get_pressed()
    FORCE = [0,0,0]
    if keys[pg.K_w]:
        FORCE[2] = MAX_FORCE
    if keys[pg.K_s]:
        FORCE[2] = -MAX_FORCE

    if keys[pg.K_d]:
        FORCE[0] = MAX_FORCE
    if keys[pg.K_a]:
        FORCE[0] = -MAX_FORCE

    if keys[pg.K_q]:
        FORCE[1] = MAX_FORCE
    if keys[pg.K_e]:
        FORCE[1] = -MAX_FORCE
    r.draw()
    pg.display.flip()
    clock.tick(FRAMERATE)


pg.quit()
r.destroy()