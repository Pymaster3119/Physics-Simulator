import tkinter
import numpy as np
import json

class TKWindow():
    def __init__(self):
        self.root = tkinter.Tk()
        self.velocity = tkinter.StringVar()
        self.beta = tkinter.StringVar()
        self.dt = tkinter.StringVar()
        self.root.title("Statistics")
        tkinter.Label(self.root, textvariable=self.velocity).pack()
        tkinter.Label(self.root, textvariable=self.beta).pack()
        tkinter.Label(self.root, textvariable=self.dt).pack()
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
                
            velnew = np.linalg.norm(np.array(CAMERAVELOCITY))
            self.velocity.set(f"{velnew} meters per second/ {LIGHTSPEED} meters per second")
            self.beta.set(f"β = {velnew / LIGHTSPEED}")
            self.dt.set(f"{dT * framerate} seconds in an second from a stationary reference frame")
        except:
            pass
        self.root.after(25, self.update_vals)

window = TKWindow()