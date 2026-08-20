import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import json
import random
import math

class SphereApp:
    def __init__(self, root):
        self.root = root
        self.root.title("3D Sky Builder")
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        self.spheres = []

        control = ttk.Frame(root, padding=10)
        control.pack(side=tk.LEFT, fill=tk.Y)

        ttk.Label(control, text="Radius Range").grid(row=0, column=0)
        ttk.Label(control, text="X Range").grid(row=1, column=0)
        ttk.Label(control, text="Y Range").grid(row=2, column=0)
        ttk.Label(control, text="Z Range").grid(row=3, column=0)
        ttk.Label(control, text="Mass Range").grid(row = 4, column = 0)
        ttk.Label(control, text="Initial Velocity Range - x").grid(row = 5, column = 0)
        ttk.Label(control, text="Initial Velocity Range - y").grid(row = 6, column = 0)
        ttk.Label(control, text="Initial Velocity Range - z").grid(row = 7, column = 0)
        ttk.Label(control, text="Number of Stars").grid(row = 8, column = 0)
        ttk.Label(control, text="Camera mass (camera is at (0,0,0))").grid(row=9, column=0)
        ttk.Label(control, text="Camera Velocity - format (vx, vy, vz)").grid(row=10, column=0)
        ttk.Label(control, text="Camera Force Control").grid(row=11, column=0)
        ttk.Label(control, text="Random star will be tracked").grid(row=12, column=0)

        self.radiusmin = tk.StringVar(value="1200000000")
        self.radiusmax = tk.StringVar(value="1600000000")
        self.cxmin = tk.StringVar(value="-25920000000")
        self.cxmax = tk.StringVar(value="25920000000")
        self.cymin = tk.StringVar(value="-25920000000")
        self.cymax = tk.StringVar(value="25920000000")
        self.czmin = tk.StringVar(value="-25920000000")
        self.czmax = tk.StringVar(value="25920000000")
        self.massmin = tk.StringVar(value="10000000")
        self.massmax = tk.StringVar(value="10000000000")
        self.vxmin = tk.StringVar(value = "-100000000")
        self.vxmax = tk.StringVar(value = "100000000")
        self.vymin = tk.StringVar(value = "-100000000")
        self.vymax = tk.StringVar(value = "100000000")
        self.vzmin = tk.StringVar(value = "-100000000")
        self.vzmax = tk.StringVar(value = "100000000")
        self.nobjects = tk.StringVar(value="100")
        self.cammass = tk.StringVar(value="0.1")
        self.camvel = tk.StringVar(value="(0, 0, 0)")
        self.camforce = tk.BooleanVar(value = True)


        ttk.Entry(control, textvariable=self.radiusmin, width=10).grid(row=0, column=1)
        ttk.Entry(control, textvariable=self.radiusmax, width=10).grid(row=0, column=2)
        ttk.Entry(control, textvariable=self.cxmin, width=10).grid(row=1, column=1)
        ttk.Entry(control, textvariable=self.cxmax, width=10).grid(row=1, column=2)
        ttk.Entry(control, textvariable=self.cymin, width=10).grid(row=2, column=1)
        ttk.Entry(control, textvariable=self.cymax, width=10).grid(row=2, column=2)
        ttk.Entry(control, textvariable=self.czmin, width=10).grid(row=3, column=1)
        ttk.Entry(control, textvariable=self.czmax, width=10).grid(row=3, column=2)
        ttk.Entry(control, textvariable=self.massmin, width=10).grid(row=4, column=1)
        ttk.Entry(control, textvariable=self.massmax, width=10).grid(row=4, column=2)
        ttk.Entry(control, textvariable=self.vxmin, width=10).grid(row=5, column=1)
        ttk.Entry(control, textvariable=self.vxmax, width=10).grid(row=5, column=2)
        ttk.Entry(control, textvariable=self.vymin, width=10).grid(row=6, column=1)
        ttk.Entry(control, textvariable=self.vymax, width=10).grid(row=6, column=2)
        ttk.Entry(control, textvariable=self.vzmin, width=10).grid(row=7, column=1)
        ttk.Entry(control, textvariable=self.vzmax, width=10).grid(row=7, column=2)
        ttk.Entry(control, textvariable=self.nobjects, width=10).grid(row=8, column=1)
        ttk.Entry(control, textvariable=self.cammass, width=10).grid(row=9, column=1)
        ttk.Entry(control, textvariable=self.camvel, width=10).grid(row=10, column=1)
        ttk.Checkbutton(control, variable=self.camforce, width=10).grid(row=11, column=1)

        ttk.Button(control, text="Generate Sky", command=self.add_sphere).grid(
            row=13, column=0, columnspan=3, pady=10, sticky="ew"
        )

        ttk.Button(control, text="Clear All", command=self.clear).grid(
            row=14, column=0, columnspan=3, sticky="ew"
        )

        self.listbox = tk.Listbox(control, width=80, height=15)
        self.listbox.grid(row=15, column=0, columnspan=3, pady=10)

        self.fig = plt.Figure(figsize=(6, 6))
        self.ax = self.fig.add_subplot(111, projection="3d")
        
        self.ax.set_xlim(float(self.cxmin.get()), float(self.cxmax.get()))
        self.ax.set_ylim(float(self.cymin.get()), float(self.cymax.get()))
        self.ax.set_zlim(float(self.czmin.get()), float(self.czmax.get()))

        self.canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.canvas.get_tk_widget().pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.redraw()

    def sphere_mesh(self, radius, cx, cy, cz):
        u = np.linspace(0, 2 * np.pi, 40)
        v = np.linspace(0, np.pi, 40)

        x = radius * np.outer(np.cos(u), np.sin(v)) + cx
        y = radius * np.outer(np.sin(u), np.sin(v)) + cy
        z = radius * np.outer(np.ones_like(u), np.cos(v)) + cz

        return x, y, z

    def add_sphere(self):
        try:
            rmin = float(self.radiusmin.get())
            rmax = float(self.radiusmax.get())
            cxmin = float(self.cxmin.get())
            cxmax = float(self.cxmax.get())
            cymin = float(self.cymin.get())
            cymax = float(self.cymax.get())
            czmin = float(self.czmin.get())
            czmax = float(self.czmax.get())
            massmin = float(self.massmin.get())
            massmax = float(self.massmax.get())
            vxmin = float(self.vxmin.get())
            vxmax = float(self.vxmax.get())
            vymin = float(self.vymin.get())
            vymax = float(self.vymax.get())
            vzmin = float(self.vzmin.get())
            vzmax = float(self.vzmax.get())
            N = int(self.nobjects.get())
        except ValueError:
            return
        for i in range(N):
            r = random.random() * (rmax-rmin) + rmin
            cx = random.random() * (cxmax-cxmin) + cxmin
            cy = random.random() * (cymax-cymin) + cymin
            cz = random.random() * (czmax-czmin) + czmin
            mass = random.random() * (massmax-massmin) + massmin
            vx = random.random() * (vxmax-vxmin) + vxmin
            vy = random.random() * (vymax-vymin) + vymin
            vz = random.random() * (vzmax-vzmin) + vzmin
            velocity = f"({vx}, {vy}, {vz})"
            self.spheres.append([r, cx, cy, cz, mass, velocity, False, False])
            self.listbox.insert(
                tk.END,
                f"R={r}, ({cx}, {cy}, {cz}), Mass={mass}, Velocity={velocity}"
            )
        self.spheres[1][7] = True

        self.redraw()

    def clear(self):
        self.spheres.clear()
        self.listbox.delete(0, tk.END)
        self.ax.set_xlim(float(self.cxmin.get()), float(self.cxmax.get()))
        self.ax.set_ylim(float(self.cymin.get()), float(self.cymax.get()))
        self.ax.set_zlim(float(self.czmin.get()), float(self.czmax.get()))
        self.redraw()

    def redraw(self):
        self.ax.clear()

        colors = plt.cm.tab10(np.linspace(0, 1, max(len(self.spheres), 1)))

        for i, (r, cx, cy, cz, mass, velocity, force, tracked) in enumerate(self.spheres):
            x, y, z = self.sphere_mesh(r, cx, cy, cz)
            self.ax.plot_surface(
                x,
                y,
                z,
                color=colors[i % len(colors)],
                edgecolor="k",
                linewidth=0.2,
                alpha=0.7,
            )

        self.ax.set_xlim(float(self.cxmin.get()), float(self.cxmax.get()))
        self.ax.set_ylim(float(self.cymin.get()), float(self.cymax.get()))
        self.ax.set_zlim(float(self.czmin.get()), float(self.czmax.get()))
        self.ax.set_box_aspect([1, 1, 1])

        if self.spheres:
            pts = []
            for r, cx, cy, cz, _, _2, _3, _4 in self.spheres:
                pts.extend([
                    (cx - r, cy - r, cz - r),
                    (cx + r, cy + r, cz + r),
                ])
            pts = np.array(pts)

            self.ax.set_xlim(float(self.cxmin.get()), float(self.cxmax.get()))
            self.ax.set_ylim(float(self.cymin.get()), float(self.cymax.get()))
            self.ax.set_zlim(float(self.czmin.get()), float(self.czmax.get()))
        else:
            self.ax.set_xlim(float(self.cxmin.get()), float(self.cxmax.get()))
            self.ax.set_ylim(float(self.cymin.get()), float(self.cymax.get()))
            self.ax.set_zlim(float(self.czmin.get()), float(self.czmax.get()))

        self.canvas.draw()

    def on_close(self):
        with open("spheres.json", "w") as txt:
            json.dump({"spheres":self.spheres, "camera": {"mass": float(self.cammass.get()),"velocity": self.camvel.get(), "forcecontrol": self.camforce.get()}}, txt)
        self.root.destroy()

root = tk.Tk()
app = SphereApp(root)
root.mainloop()