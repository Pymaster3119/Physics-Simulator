import tkinter
import numpy as np
import json

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
        tkinter.Label(self.root, textvariable=self.velocity).pack()
        tkinter.Label(self.root, textvariable=self.beta).pack()
        tkinter.Label(self.root, textvariable=self.dt).pack()
        tkinter.Label(self.root, textvariable=self.framerate).pack()
        tkinter.Label(self.root, textvariable=self.force).pack()
        tkinter.Label(self.root, textvariable=self.acc).pack()
        self.update_vals()
        self.root.mainloop()

    def update_vals(self):
        try:
            with open("simulatorstats.json", 'r') as txt:
                data = json.load(txt)
                CAMERAVELOCITY = data["CAMERAVELOCITY"]
                LIGHTSPEED = data["LIGHTSPEED"]
                dT = data["DELTATIME"]
                framerate = data["FRAMERATE"]
                force = data["FORCE"]
                acc = data["ACC"]
                
            velnew = np.linalg.norm(np.array(CAMERAVELOCITY))
            self.velocity.set(f"{velnew} meters per second/ {LIGHTSPEED} meters per second")
            self.beta.set(f"β = {velnew / LIGHTSPEED}")
            self.dt.set(f"1 second for you is {dT * framerate} seconds in a stationary reference frame")
            self.framerate.set(f"Running at framerate {framerate}")
            self.force.set(f"Force of {force} applied")
            self.acc.set(f"Acceleration of {acc}")
        except:
            pass
        self.root.after(25, self.update_vals)

window = TKWindow()