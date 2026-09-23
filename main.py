import multiprocessing
from pathlib import Path
import tkinter as tk


def simworker():
    import simulation
def statsworker():
    import Statswindow
def starworker():
    import createstars


def start_simulation(filename):
    with open("Scenarios/" + filename + ".json", "r") as txt1:
        text = txt1.readlines()
        with open("spheres.json", "w") as txt2:
            txt2.writelines(text)
    with open("simulatorstats.json", "w") as txt:
        txt.write("GO!")
    global root

    if root is not None:
        root.quit()
        root.destroy()
        root.update()

    p1 = multiprocessing.Process(target=simworker)
    p2 = multiprocessing.Process(target=statsworker)

    p1.start()
    p2.start()

    p1.join()
    with open("simulatorstats.json", "w") as txt:
        txt.write("SHUTDOWN")
    load_file_selector()

def start_starcreation():
    global root

    if root is not None:
        root.quit()
        root.destroy()
        root.update()

    p1 = multiprocessing.Process(target=starworker)

    p1.start()

    p1.join()
    load_file_selector()

root = None


def load_file_selector():
    global root

    root = tk.Tk()
    root.title("Aditya's GSET Physics Simulator - Main Menu")

    frame = tk.Frame(root)
    frame.pack(padx=12, pady=12)

    dir_path = Path("Scenarios")

    tk.Label(frame, text="Scenes:").grid(row=0, column=0, sticky="w", pady=(0, 8))

    for idx, file_path in enumerate(sorted(dir_path.iterdir())):
        if file_path.is_file():
            filename = file_path.name.replace(".json", "")
            tk.Button(
                frame,
                text=filename,
                command=lambda name=filename: start_simulation(name)
            ).grid(row=idx + 1, column=0, sticky="w", pady=2)

    tk.Label(frame, text="="*33).grid(row = len(sorted(dir_path.iterdir())) + 9, column=0, sticky="w", pady=2)
    tk.Button(frame, text="Generate New Night Sky Scene", command=start_starcreation).grid(row = len(sorted(dir_path.iterdir())) + 10, column=0, sticky="w", pady=2)

    root.mainloop()


if __name__ == "__main__":
    load_file_selector()