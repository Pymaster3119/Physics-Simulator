import multiprocessing
import os

def simworker():
    import simulation
def statsworker():
    import Statswindow

if __name__ == "__main__":
    # 1. Initialize the process with a target function and arguments
    p1 = multiprocessing.Process(target=simworker)
    p2 = multiprocessing.Process(target=statsworker)
    
    # 2. Start execution (spawns the new OS process)
    p1.start()
    p2.start()
    
    # 3. Wait for processes to finish before continuing main code
    p1.join()
    print("Main window quit!")
    p2.interrupt()