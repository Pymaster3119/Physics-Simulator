import pygame as pg
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import numpy as np
import math
import readspheres
import re
import tkinter
import time


SCREEN_SIZE = (500, 500)

WINDOW_CREATION_FLAGS = pg.OPENGL | pg.DOUBLEBUF
FRAMERATE = 30
DATA_TYPE_COLORED_VERTEX = np.dtype({
    'formats': [np.float32, np.float32, np.float32],
    'offsets': [0, 4, 8],
    'names': ['x','y','z'],
    'itemsize': 12})

CAMERAPOSITION = [0,0,0]
CAMERAROTATION = [0.05,0.05,0]
FORCE = [0,0,0]
MAX_FORCE = 1e14
LIGHTSPEED = 299792458
CAMERAVELOCITY = [0,0,0]
ROTMAT = None
TRACKED_STAR = 0


timeBetweenFrames = 1/FRAMERATE
frameStartTime = time.time_ns()

pg.init()
pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 3)
pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 3)
pg.display.gl_set_attribute(pg.GL_CONTEXT_PROFILE_MASK, pg.GL_CONTEXT_PROFILE_CORE)
pg.mouse.set_visible(False)
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
        self.velocity_buffer_loc = glGetUniformLocation(self.shader, "u_star_velocities")
        self.tracked_star_loc = glGetUniformLocation(self.shader, "u_trackedStar")
        self.cameramass, self.cameravelocity, self.cameraforce = readspheres.read_cam()
        self.points = readspheres.get_full_points()
        match = re.match(r"^\(([^,]+),([^,]+),([^,]+)\)$", self.cameravelocity)
        self.dT = (1/FRAMERATE)
        self.referenceFrameDT = (1/FRAMERATE)
        self.acc = [0,0,0]
        self.trackedDt = 0
        self.trackedV = 0
        self.tmass = 0
        self.cspacetimediagram = []
        self.tstartpostion = None
        self.totaltime = 0
        self.tspacetimediagram = []
        if match:
            vx, vy, vz = match.groups()
            vx = float(vx)
            vy = float(vy)
            vz = float(vz)
            self.cameravelocity = [vx, vy, vz]
        else:
            raise Exception("One of the velocity strings is not correct: " + self.cameravelocity)

    def parseVelocities(self, str):
        match = re.match(r"^\(([^,]+),([^,]+),([^,]+)\)$", str)
        if match:
            vx, vy, vz = match.groups()
        else:
            raise Exception("One of the velocity strings is not correct: " + str)

        return [float(vx), float(vy), float(vz)]
    def update_point(self, point):
        x,y,z,r,mass,velocity, force_controlled_by_keyboard, tracked = point
        if tracked and self.tstartpostion is None:
            self.tstartpostion = np.array((x,y,z))
        
        vx, vy, vz = self.parseVelocities(velocity.strip())
        v = np.linalg.norm(np.array([vx,vy,vz]))
        dt = self.referenceFrameDT * math.sqrt(1 - ((v**2)/(LIGHTSPEED**2)))
        x += dt * float(vx)
        y += dt * float(vy)
        z += dt * float(vz)

        if tracked:
            self.trackedDt = dt
            self.trackedV = v
            self.tmass = mass
            self.totaltime += self.referenceFrameDT
            self.tspacetimediagram.append((np.linalg.norm(np.array([x,y,z]) - self.tstartpostion) / 299_792_458,self.totaltime))
        
        return [x,y,z,r,mass,velocity, force_controlled_by_keyboard, tracked]
    
    def update_points(self):
        global CAMERAPOSITION, CAMERAVELOCITY, timeBetweenFrames
        # CALCULATE WORLD DELTATIME
        self.dT = timeBetweenFrames / 1e9
        print(self.dT)
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
            f = np.array(FORCE)
            if np.linalg.norm(f) != 0:
                v = np.array(CAMERAVELOCITY)
                funit = f / np.linalg.norm(f)
                v_parallel = np.dot(v, funit) * funit
                v_perp = v - v_parallel
                v_parallel = np.dot(v,funit)
                v_perp = np.linalg.norm(v_perp)
                v_par_vec = np.dot(v, funit) * funit
                v_perp_vec = v - v_par_vec
                norm_v_perp = np.linalg.norm(v_perp_vec)
                u_perp = v_perp_vec / norm_v_perp if norm_v_perp > 1e-10 else None

                #Calculate inital momenta
                pOparallel = self.cameramass * v_parallel / math.sqrt(1 - (np.linalg.norm(v)**2 / LIGHTSPEED ** 2))
                pOperp = self.cameramass * v_perp / math.sqrt(1 - (np.linalg.norm(v)**2 / LIGHTSPEED ** 2))
                

                #Calculate updated velocities
                vparallel = (LIGHTSPEED * ((pOparallel + np.linalg.norm(f) * self.referenceFrameDT))) / math.sqrt(((self.cameramass**2 * LIGHTSPEED**2) + ((pOparallel + np.linalg.norm(f) * self.referenceFrameDT)** 2) + pOperp ** 2))
                vperp = (pOperp * LIGHTSPEED) / math.sqrt(self.cameramass**2*LIGHTSPEED**2 + (pOparallel +np.linalg.norm(f)*self.referenceFrameDT)**2 + pOperp**2)
                if u_perp is not None:
                    vprime = vparallel * funit + vperp * u_perp
                else:
                    vprime = vparallel * funit
                vx = vprime[0]
                vy = vprime[1]
                vz = vprime[2]

                #Calculate updated accelerations
                aparallel = (LIGHTSPEED * np.linalg.norm(f) * (self.cameramass**2*LIGHTSPEED**2 + pOperp**2))/(self.cameramass**2 * LIGHTSPEED**2 + (pOparallel + np.linalg.norm(f) * self.referenceFrameDT)**2 + pOperp**2)**1.5
                aperp = (-pOperp * LIGHTSPEED * np.linalg.norm(f) * (pOparallel + np.linalg.norm(f) * self.referenceFrameDT)) / ((self.cameramass**2*LIGHTSPEED**2 + (pOparallel+np.linalg.norm(f)*self.referenceFrameDT)**2 + pOperp**2)**1.5)
                if u_perp is not None:
                    aprime = aparallel * funit + aperp * u_perp
                else:
                    aprime = aparallel * funit
                self.acc = [aprime[0], aprime[1], aprime[2]]


                #Calculate updated position
                xparallel = LIGHTSPEED * math.sqrt(self.cameramass**2 * LIGHTSPEED**2 + (pOparallel+np.linalg.norm(f) * self.referenceFrameDT)**2 + pOperp**2) / np.linalg.norm(f)
                xparallel -= LIGHTSPEED * math.sqrt(self.cameramass**2 * LIGHTSPEED**2 + (pOparallel)**2 + pOperp**2) / np.linalg.norm(f)
                xperp = (pOperp * LIGHTSPEED / np.linalg.norm(f)) * math.asinh((pOparallel + np.linalg.norm(f)*self.referenceFrameDT)/(math.sqrt(self.cameramass**2*LIGHTSPEED**2 + pOperp**2)))
                xperp -= (pOperp * LIGHTSPEED / np.linalg.norm(f)) * math.asinh((pOparallel)/(math.sqrt(self.cameramass**2*LIGHTSPEED**2 + pOperp**2)))
                if u_perp is not None:
                    xprime = xparallel * funit + xperp * u_perp
                else:
                    xprime = xparallel * funit
                CAMERAPOSITION = [CAMERAPOSITION[0] + xprime[0], CAMERAPOSITION[1] + xprime[1], CAMERAPOSITION[2] + xprime[2]]

                self.cameravelocity = [vx, vy, vz]
                CAMERAVELOCITY = self.cameravelocity

            else:
                self.acc = [0,0,0]
            
                cx += self.referenceFrameDT * float(vx)
                cy += self.referenceFrameDT * float(vy)
                cz += self.referenceFrameDT * float(vz)
                CAMERAPOSITION = (cx, cy, cz)
                self.cameravelocity = [vx, vy, vz]
                CAMERAVELOCITY = self.cameravelocity
        else:
            self.acc = [0,0,0]
        
            cx += self.referenceFrameDT * float(vx)
            cy += self.referenceFrameDT * float(vy)
            cz += self.referenceFrameDT * float(vz)
            CAMERAPOSITION = (cx, cy, cz)
            self.cameravelocity = [vx, vy, vz]
            CAMERAVELOCITY = self.cameravelocity
        self.tspacetimediagram.append((np.linalg.norm(np.array(CAMERAPOSITION) - np.array([0,0,0])) / 299_792_458,self.totaltime))

    def calculate_length_contraction(self, star_point):
        global CAMERAPOSITION, CAMERAVELOCITY
        x,y,z,r,mass,velocity, force_controlled_by_keyboard, tracked = star_point
        velocity = np.array(self.parseVelocities(velocity))
        cameravel = np.array(CAMERAVELOCITY)
        relative_position = np.array([x - CAMERAPOSITION[0], y - CAMERAPOSITION[1], z-CAMERAPOSITION[2]])

        #3-D addition of forces relativistically
        v = cameravel/np.linalg.norm(cameravel)
        starvelparalel = np.dot(velocity, v)
        relativeparalelvel = (starvelparalel - np.linalg.norm(cameravel)) / (1 - (starvelparalel * np.linalg.norm(cameravel))/(LIGHTSPEED**2))
        starvelperp = velocity - starvelparalel * v
        gammav = 1/math.sqrt(1 - (np.linalg.norm(cameravel) ** 2)/(LIGHTSPEED ** 2))
        relativeperpvel = starvelperp / (gammav * (1 - (starvelparalel * np.linalg.norm(cameravel))/(LIGHTSPEED ** 2)))
        relativevelocity = relativeparalelvel * v + relativeperpvel

        if np.linalg.norm(cameravel) == 0:
            relativevelocity = velocity

        #Calculate length contraction
        relative_speed = np.linalg.norm(relativevelocity)
        gamma = 0
        velocity_hat = 0
        if relative_speed == 0:
            gamma = 1
            velocity_hat = np.array([1.0,0.0,0.0])
        else:
            velocity_hat = relativevelocity / relative_speed
            gamma = 1/math.sqrt(1-((relative_speed**2)/(LIGHTSPEED**2)))
        return velocity_hat[0], velocity_hat[1], velocity_hat[2], gamma


        
    def write_to_json(self):
        with open("simulatorstats.json", "w") as txt:
            readspheres.json.dump({"CAMERAVELOCITY": CAMERAVELOCITY, "LIGHTSPEED": LIGHTSPEED, "DELTATIME": self.referenceFrameDT, "FRAMERATE": 1/(timeBetweenFrames/1e9), "FORCE": FORCE, "ACC": self.acc, "TRACKEDOBJDT": self.trackedDt, "TRACKEDOBJV": self.trackedV, "MASS": self.cameramass, "TMASS": self.tmass, "CPOINTS": self.cspacetimediagram, "TPOINTS": self.tspacetimediagram}, txt)

    def draw(self):
        global timeBetweenFrames, frameStartTime, ROTMAT, TRACKED_STAR
        #Update framerate and points
        currentTime = time.time_ns()
        timeBetweenFrames = currentTime - frameStartTime
        frameStartTime = currentTime
        self.update_points()

        #Populate points matrix & upload to GPU
        N = len(self.points)
        points = [[i[0] - CAMERAPOSITION[0], i[1] - CAMERAPOSITION[1], i[2] - CAMERAPOSITION[2], i[3]] for i in self.points]
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

        #Populate the distances matrix & upload to GPU
        distances = [self.calculate_length_contraction(i) for i in self.points]
        # Upload distances (vx, vy, vz, gamma) as a texture buffer — DO NOT divide by 1e12
        dist_data = np.array(distances, dtype=np.float32)
        dist_data = dist_data.reshape((-1,4))

        buf2 = glGenBuffers(1)
        glBindBuffer(GL_TEXTURE_BUFFER, buf2)
        glBufferData(GL_TEXTURE_BUFFER, dist_data.nbytes, dist_data, GL_STATIC_DRAW)

        tex2 = glGenTextures(1)
        texture_unit2 = 1
        glActiveTexture(GL_TEXTURE0 + texture_unit2)
        glBindTexture(GL_TEXTURE_BUFFER, tex2)
        glTexBuffer(GL_TEXTURE_BUFFER, GL_RGBA32F, buf2)

        glClear(GL_COLOR_BUFFER_BIT)
        glUseProgram(self.shader)

        # Now that the program is active, set sampler and other uniforms
        glUniform1i(self.point_buffer_loc, texture_unit)
        glUniform1i(self.velocity_buffer_loc, texture_unit2)
        glUniform1i(self.point_count_loc, N)
        glUniform1f(self.widthloc, SCREEN_SIZE[0])
        glUniform1f(self.heightloc, SCREEN_SIZE[1])
        glUniform3fv(self.cameraPosLoc, 1, np.array(CAMERAPOSITION) / 1e+12)
        glUniform3fv(self.cameraAngleLoc, 1, CAMERAROTATION)
        glUniformMatrix3fv(self.matrixLoc, 1, True, ROTMAT)
        glUniform1f(self.tracked_star_loc, TRACKED_STAR)
        self.mesh.draw()
        self.write_to_json()

    def destroy(self):
        self.mesh.destroy()
        glDeleteProgram(self.shader)

running = True
r = Renderer()
pg.mouse.set_pos(SCREEN_SIZE[0]/2,SCREEN_SIZE[1]/2)
for idx, i in enumerate(r.points):
    if i[7]:
        TRACKED_STAR = idx

while running:
    pg.event.set_grab(True)
    rot = pg.mouse.get_rel()
    CAMERAROTATION = [(CAMERAROTATION[0] + 0.05 * rot[1]), (CAMERAROTATION[1] + 0.05 * rot[0]),0]
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

    if keys[pg.K_UP]:
        CAMERAROTATION[0] -= 0.3
    if keys[pg.K_DOWN]:
        CAMERAROTATION[0] += 0.3
    if keys[pg.K_LEFT]:
        CAMERAROTATION[1] -= 0.3
    if keys[pg.K_RIGHT]:
        CAMERAROTATION[1] += 0.3

    if keys[pg.K_ESCAPE]:
        pg.quit()
        r.destroy()
        break

    #Calculate rotation matrices
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

    ROTMAT = maty @ matx
    r.draw()
    pg.display.flip()
    clock.tick(FRAMERATE)
    pg.mouse.set_pos(SCREEN_SIZE[0]/2,SCREEN_SIZE[1]/2)


pg.quit()
r.destroy()