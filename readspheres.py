import json
import numpy as np
def read_spheres():
    with open("spheres.json", "r") as txt:
        spheres = json.load(txt)["spheres"]
    points_tot = np.zeros((len(spheres), 4), dtype=np.float32)
    num_points = 0
    for i in spheres:
        radius = i[0]
        cx = i[1]
        cy = i[2]
        cz = i[3]
        

        points_tot[num_points] = np.array([cx, cy, cz, radius])

    return points_tot

def get_full_points():
    with open("spheres.json", "r") as txt:
        spheres = json.load(txt)["spheres"]
    points_tot = []
    num_points = 0
    for i in spheres:
        radius = i[0]
        cx = i[1]
        cy = i[2]
        cz = i[3]
        mass = i[4]
        velocity = i[5]
        force = i[6]
        tracked = i[7]
        
        points_tot.append([cx, cy, cz, radius, mass, velocity, force,tracked])

    return points_tot

def read_cam():
    with open("spheres.json", "r") as txt:
            cam = json.load(txt)["camera"]
    mass = cam["mass"]
    velocity = cam["velocity"]
    force = cam["forcecontrol"]

    return (mass, velocity, force)

if __name__ == "__main__":
    print(read_spheres().shape)
    print(read_cam())