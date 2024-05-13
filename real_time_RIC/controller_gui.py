import tkinter as tk
from subprocess import Popen
import redis

# Establish a Redis connection
r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

def start_p1():
    processes['P1'] = Popen(['sudo', '-E', 'python3', 'dashboard_perUE.py'])

def stop_p1():
    if 'P1' in processes:
        processes['P1'].kill()
        processes.pop('P1')

def start_p2():
    processes['P2'] = Popen(['sudo', 'python3', 'edgeric_run_scheduling.py'])

def stop_p2():
    if 'P2' in processes:
        processes['P2'].kill()
        processes.pop('P2')

def start_p3():
    processes['P3'] = Popen(['sudo', '-E', 'python3', 'dashboard_aggregate.py'])

def stop_p3():
    if 'P3' in processes:
        processes['P3'].kill()
        processes.pop('P3')        

def update_algorithm(selection):
    # Here we write the selected algorithm to Redis
    r.set('scheduling_algorithm', selection)
    print(f"Algorithm set to {selection}")

def update_rl_model(selection):
    # Write the selected RL model to Redis
    r.set('rl_scheduling_model', selection)
    print(f"RL Model set to {selection}")

app = tk.Tk()
app.title("EdgeRIC Controller")

# Buttons for starting and stopping processes
start_p1_btn = tk.Button(app, text="Start Per UE metrics dashboard", command=start_p1)
start_p1_btn.pack(pady=5)
stop_p1_btn = tk.Button(app, text="Stop P1", command=stop_p1)
stop_p1_btn.pack(pady=5)
start_p2_btn = tk.Button(app, text="μApp1: Start Downlink scheduling microApp", command=start_p2)
start_p2_btn.pack(pady=5)
stop_p2_btn = tk.Button(app, text="Stop μApp1", command=stop_p2)
stop_p2_btn.pack(pady=5)
start_p3_btn = tk.Button(app, text="Start aggregate statistics dashboard", command=start_p3)
start_p3_btn.pack(pady=5)
stop_p3_btn = tk.Button(app, text="Stop P3", command=stop_p3)
stop_p3_btn.pack(pady=5)


# Dropdown menu for selecting scheduling algorithms
algorithm_var = tk.StringVar(app)
algorithm_var.set("Select Traditional Scheduling Algorithm")  # default value
algorithms = ["Max CQI", "Max Weight", "Proportional Fair (PF)", "Round Robin", "RL"]
algorithm_menu = tk.OptionMenu(app, algorithm_var, *algorithms, command=update_algorithm)
algorithm_menu.pack(pady=5)

# Dropdown menu for selecting RL models
rl_model_var = tk.StringVar(app)
rl_model_var.set("Select Scheduling with RL")  # default value
rl_models = ["Initial Model", "Half Trained Model", "Fully Trained Model"]
rl_model_menu = tk.OptionMenu(app, rl_model_var, *rl_models, command=update_rl_model)
rl_model_menu.pack(pady=5)

app.mainloop()
