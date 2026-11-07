import tkinter as tk

root = tk.Tk()

label = tk.Label(root, text= '''
Welcome to my GSET Physics Simulator!!
This includes the relativistic concepts that we looked at in GSET in a space setting, such as:
- Time dialation
- Length contraction
- Relativistic acceleration
- Momentum & energy adjustments
- Relative velocity adjustments

Future improvements/limitations:
- Information from photons is assumed to travel instantly
- GUI improvements are planned

====================================================================================================================================

The app comes with many scenarios, listed on the top of the screen you just came from.
Each one has many different stars, modelled as perfect spheres, that can all have a motion to them.
When you click on a window and give it a few seconds to load, a few things will open:
1. The simulation window
2. The statistics window

====================================================================================================================================

In the simulation window, you can control your camera and see these stars move.
W and S apply force in the +x and -x axes respectively
D and A apply force in the +z and -z axes respectively
Q and E apply force in the +y and -y axes respectively

The mouse can be used to rotate along pitch and yaw axes.
Time and distances shown in this app reflect what a person moving along the camera's path would be expected to see.
These stars can collide with each other (all collisions are perfectly elastic).

To exit, open the simulation window and hit escape.

====================================================================================================================================

With the simulation window, the statistics window will open. You will see your velocity, beta (v/c), and framerate.
The time experienced in a stationary reference frame (relative to the program coordinate system) for every second you experience is shown.
Force and acceleration vectors are displayed below that.

There is an object in the simulation shaded in red rather than white. This is your "tracked object" that recieves additional stats.
For both the camera and tracked object, the following stats are shown:
1. Time passed for that object in one camera-second
2. Beta for that object
3. The object's momentum
4. The object's energy

Below that, a spacetime curve is shown. Distances here are measured in light-seconds. 
The blue line represents the camera while the red line is the tracked object.

To get back, hit escape or close this window.
''', justify="left")

label.pack()

root.bind("<Escape>", lambda event: root.destroy())

root.mainloop()