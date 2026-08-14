import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import json

class SphereApp:
    def __init__(self, root):
        self.root = root
        self.root.title("3D Scene Builder")
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        self.spheres = []

        control = ttk.Frame(root, padding=10)
        control.pack(side=tk.LEFT, fill=tk.Y)

        ttk.Label(control, text="Radius").grid(row=0, column=0)
        ttk.Label(control, text="Center X").grid(row=1, column=0)
        ttk.Label(control, text="Center Y").grid(row=2, column=0)
        ttk.Label(control, text="Center Z").grid(row=3, column=0)
        ttk.Label(control, text="Mass").grid(row = 4, column = 0)
        ttk.Label(control, text="Initial Velocity - format (vx, vy, vz)").grid(row = 5, column = 0)
        ttk.Label(control, text="Force Controlled by Keyboard?").grid(row = 6, column = 0)
        ttk.Label(control, text="Camera mass (camera is at (0,0,0))").grid(row=7, column=0)
        ttk.Label(control, text="Camera Velocity - format (vx, vy, vz)").grid(row=8, column=0)
        ttk.Label(control, text="Camera Force Control").grid(row=9, column=0)

        self.radius = tk.StringVar(value="1")
        self.cx = tk.StringVar(value="0")
        self.cy = tk.StringVar(value="0")
        self.cz = tk.StringVar(value="0")
        self.mass = tk.StringVar(value="0.1")
        self.velocity = tk.StringVar(value="(0, 0, 0)")
        self.force = tk.BooleanVar(value = False)
        self.cammass = tk.StringVar(value="0.1")
        self.camvel = tk.StringVar(value="(0, 0, 0)")
        self.camforce = tk.BooleanVar(value = True)


        ttk.Entry(control, textvariable=self.radius, width=10).grid(row=0, column=1)
        ttk.Entry(control, textvariable=self.cx, width=10).grid(row=1, column=1)
        ttk.Entry(control, textvariable=self.cy, width=10).grid(row=2, column=1)
        ttk.Entry(control, textvariable=self.cz, width=10).grid(row=3, column=1)
        ttk.Entry(control, textvariable=self.mass, width=10).grid(row=4, column=1)
        ttk.Entry(control, textvariable=self.velocity, width=10).grid(row=5, column=1)
        ttk.Checkbutton(control, variable=self.force, width=10).grid(row=6, column=1)
        ttk.Entry(control, textvariable=self.cammass, width=10).grid(row=7, column=1)
        ttk.Entry(control, textvariable=self.camvel, width=10).grid(row=8, column=1)
        ttk.Checkbutton(control, variable=self.camforce, width=10).grid(row=9, column=1)

        ttk.Button(control, text="Add Sphere", command=self.add_sphere).grid(
            row=10, column=0, columnspan=2, pady=10, sticky="ew"
        )

        ttk.Button(control, text="Clear All", command=self.clear).grid(
            row=11, column=0, columnspan=2, sticky="ew"
        )

        self.listbox = tk.Listbox(control, width=80, height=15)
        self.listbox.grid(row=12, column=0, columnspan=2, pady=10)

        self.fig = plt.Figure(figsize=(6, 6))
        self.ax = self.fig.add_subplot(111, projection="3d")
        
        self.ax.set_xlim(-25920000000, 25920000000)
        self.ax.set_ylim(-25920000000, 25920000000)
        self.ax.set_zlim(-25920000000, 25920000000)

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
            r = float(self.radius.get())
            cx = float(self.cx.get())
            cy = float(self.cy.get())
            cz = float(self.cz.get())
            mass = float(self.mass.get())
            velocity = self.velocity.get()
            force = self.force.get()
        except ValueError:
            return

        self.spheres.append((r, cx, cy, cz, mass, velocity, force))
        self.listbox.insert(
            tk.END,
            f"R={r}, ({cx}, {cy}, {cz}), Mass={mass}, Velocity={velocity}, Keyboard-controled Force: {force}"
        )
        self.redraw()

    def clear(self):
        self.spheres.clear()
        self.listbox.delete(0, tk.END)
        self.ax.set_xlim(-25920000000, 25920000000)
        self.ax.set_ylim(-25920000000, 25920000000)
        self.ax.set_zlim(-25920000000, 25920000000)
        self.redraw()

    def redraw(self):
        self.ax.clear()

        colors = plt.cm.tab10(np.linspace(0, 1, max(len(self.spheres), 1)))

        for i, (r, cx, cy, cz, mass, velocity, force) in enumerate(self.spheres):
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

        self.ax.set_xlabel("X")
        self.ax.set_ylabel("Y")
        self.ax.set_zlabel("Z")
        self.ax.set_box_aspect([1, 1, 1])

        if self.spheres:
            pts = []
            for r, cx, cy, cz, _, _2, _3 in self.spheres:
                pts.extend([
                    (cx - r, cy - r, cz - r),
                    (cx + r, cy + r, cz + r),
                ])
            pts = np.array(pts)

            self.ax.set_xlim(-25920000000, 25920000000)
            self.ax.set_ylim(-25920000000, 25920000000)
            self.ax.set_zlim(-25920000000, 25920000000)
        else:
            self.ax.set_xlim(-25920000000, 25920000000)
            self.ax.set_ylim(-25920000000, 25920000000)
            self.ax.set_zlim(-25920000000, 25920000000)

        self.canvas.draw()

    def on_close(self):
        with open("spheres.json", "w") as txt:
            json.dump({"spheres":self.spheres, "camera": {"mass": float(self.cammass.get()),"velocity": self.camvel.get(), "forcecontrol": self.camforce.get()}}, txt)
        self.root.destroy()

root = tk.Tk()
app = SphereApp(root)
root.mainloop()