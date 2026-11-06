import tkinter
import numpy as np
import json
import math
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class TKWindow():
    def __init__(self):
        self.root = tkinter.Tk()
        self.velocity = tkinter.StringVar()
        self.beta = tkinter.StringVar()
        self.dt = tkinter.StringVar()
        self.framerate = tkinter.StringVar()
        self.force = tkinter.StringVar()
        self.acc = tkinter.StringVar()
        self.root.title("Statistics")
        self.root.geometry("800x800")
        self.trackedObjectDt = tkinter.StringVar(value = "1 second for you is 1 second for the camera")
        self.trackedObjectB = tkinter.StringVar()
        self.camMomentum = tkinter.StringVar()
        self.camEnergy = tkinter.StringVar()
        self.trackedObjectMomentum = tkinter.StringVar()
        self.trackedObjectEnergy = tkinter.StringVar()
        tkinter.Label(self.root, textvariable=self.velocity).pack()
        tkinter.Label(self.root, textvariable=self.beta).pack()
        tkinter.Label(self.root, textvariable=self.dt).pack()
        tkinter.Label(self.root, textvariable=self.framerate).pack()
        tkinter.Label(self.root, textvariable=self.force).pack()
        tkinter.Label(self.root, textvariable=self.acc).pack()
        self.trackingframe = tkinter.Frame(self.root)
        tkinter.Label(self.trackingframe, text="Camera").grid(row=0, column = 0)
        tkinter.Label(self.trackingframe, text="1 second for you is 1 second for the camera").grid(row=1, column = 0)
        tkinter.Label(self.trackingframe, textvariable=self.beta).grid(row=2, column=0)
        tkinter.Label(self.trackingframe, textvariable=self.camMomentum).grid(row=3, column=0)
        tkinter.Label(self.trackingframe, textvariable=self.camEnergy).grid(row=4, column=0)
        self.cameracanvas = None
        self.cfig = None
        self.cax = None

        tkinter.Label(self.trackingframe, text="Tracked object").grid(row=0, column = 1)
        tkinter.Label(self.trackingframe, textvariable=self.trackedObjectDt).grid(row=1, column = 1)
        tkinter.Label(self.trackingframe, textvariable=self.trackedObjectB).grid(row=2, column=1)
        tkinter.Label(self.trackingframe, textvariable=self.trackedObjectMomentum).grid(row=3, column=1)
        tkinter.Label(self.trackingframe, textvariable=self.trackedObjectEnergy).grid(row=4, column=1)
        self.trackingframe.pack()
        self.update_vals()
        self.root.mainloop()

    def shutdown(self):
        self.root.quit()
        self.root.destroy()

    def update_vals(self):
        try:
            with open("simulatorstats.json", 'r') as txt:
                try:
                    data = json.load(txt)
                    CAMERAVELOCITY = data["CAMERAVELOCITY"]
                    LIGHTSPEED = data["LIGHTSPEED"]
                    dT = data["DELTATIME"]
                    framerate = data["FRAMERATE"]
                    force = data["FORCE"]
                    acc = data["ACC"]
                    todt = data["TRACKEDOBJDT"]
                    tov = data["TRACKEDOBJV"]
                    mass = data["MASS"]
                    tmass = data["TMASS"]
                    cpoints = data["CPOINTS"]
                    tpoints = data["TPOINTS"]
                except Exception as e:
                    with open("simulatorstats.json", "r") as txt2:
                        if txt2.readline()=="SHUTDOWN":
                            self.shutdown()
                            return
                                   
            velnew = np.linalg.norm(np.array(CAMERAVELOCITY))
            self.velocity.set(f"{velnew} meters per second/ {LIGHTSPEED} meters per second")
            self.beta.set(f"β = {velnew / LIGHTSPEED}")
            self.trackedObjectB.set(f"β = {tov / LIGHTSPEED}")
            self.dt.set(f"1 second for you is {dT * framerate} seconds in a stationary reference frame")
            self.framerate.set(f"Running at framerate {framerate}")
            self.force.set(f"Force of {force} applied")
            self.acc.set(f"Acceleration of {acc}")
            self.trackedObjectDt.set(f"1 second for you is {todt * framerate} seconds for the tracked object")
            cgamma = 1/math.sqrt(1- (velnew / LIGHTSPEED)**2)
            tgamma = 1/math.sqrt(1- (tov / LIGHTSPEED)**2)
            self.camMomentum.set(f"Momentum: {velnew * mass * cgamma}")
            self.trackedObjectMomentum.set(f"Momentum: {tov * tmass * tgamma}")
            self.camEnergy.set(f"Energy: {(cgamma - 1) * mass * LIGHTSPEED**2}")
            self.trackedObjectEnergy.set(f"Energy: {(tgamma - 1) * tmass * LIGHTSPEED**2}")

            #Plot space-time diagram
            c_x = [i[0] for i in cpoints]
            c_y = [i[1] for i in cpoints]
            t_x = [i[0] for i in tpoints]
            t_y = [i[1] for i in tpoints]
            if self.cameracanvas is None:
                self.cfig = Figure(figsize=(5, 4), dpi=100)
                self.cax = self.cfig.add_subplot(111)
                self.cax.plot(c_x, c_y, marker='o', color='red', linestyle='')
                self.cax.plot(t_x, t_y, marker='o', color='blue', linestyle='')
                _, x_max = self.cax.get_xlim()
                _, y_max = self.cax.get_ylim()
                largest_max = max(x_max, y_max)
                self.cax.set_xlim(0, largest_max)
                self.cax.set_ylim(0, largest_max)
                self.cameracanvas = FigureCanvasTkAgg(self.cfig, master=self.trackingframe)
                self.cameracanvas.draw()
                self.cameracanvas.get_tk_widget().grid(row=5, column = 0, columnspan=2)
            else:
                self.cax.clear()
                self.cax.plot(c_x, c_y, marker='o', color='red', linestyle='')
                self.cax.plot(t_x, t_y, marker='o', color='blue', linestyle='')
                _, x_max = self.cax.get_xlim()
                _, y_max = self.cax.get_ylim()
                largest_max = max(x_max, y_max)
                self.cax.set_xlim(0, largest_max)
                self.cax.set_ylim(0, largest_max)
                self.cax.set_xlabel("Distance from starting position (light-seconds)")
                self.cax.set_ylabel("Time relative to stationary reference frame (seconds)")
                self.cax.set_title("Spacetime Curve")
                self.cameracanvas.draw()

        except Exception as e:
            pass
        self.root.after(25, self.update_vals)

window = TKWindow()