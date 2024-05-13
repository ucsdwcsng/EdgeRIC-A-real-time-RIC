## Usage
```bash
sudo python3 muApp1_run_DL_scheduling.py
```
## Setting the scheduler algorithm manually
Use redis database to update what algorithm to run:
```bash
# Establish a Redis connection
r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
r.set('scheduling_algorithm', selection)  # selection can be: Max CQI, Max Weight,
                                          # Proportional Fair (PF), Round Robin, RL 
```
If the algorithm selected is RL, set the directory for the RL model
```bash
 r.set('rl_scheduling_model', selection)  # selection can be Initial Model,
                                          # Half Trained Model, Fully Trained Model
```
The respective models are saved in:
```bash
├── ../rl_model/           
    ├── initial_model 
      ├──model_demo.pt
    ├── half_trained_model 
      ├──model_demo.pt
    ├── fully_trained_model 
      ├──model_demo.pt
```
      
## μApps supported
```bash
├── /muApp1           # weight based abstraction of downlink scheduling control
│   ├── muApp1_run_DL_scheduling.py
├── /muApp2           # training an RL agent to compute downlink scheduling policy
    ├── muApp2_train_RL_DL_scheduling.py
├── /muApp3           # training an RL agent to compute downlink scheduling policy
    ├── metrics_monitor_aggregate.py # launch dashboard for aggregate statistics
    ├── metrics_monitor_perUE.py     # launch dashboard for per UE metrics

```

## How to launch the EdgeRIC controller gui
This controller gui lets you manage μApps, such as start and stop a specific μApp.
```bash
sudo python3 controller_gui.py
```
To launch the DL scheduling μApp:
- **Start μApp1** 
  - **Choose the algorithm you want to run**
    - **If traditional:** Choose between Max CQI, Max Weight, PF, Round Robin
    - **If RL:** Specify the directory for the saved RL model [Please Note: the RL scheduler is specific to number of UEs the system started with, refer to the paper]

To launch the training of an RL scheduling μApp policy:
- **Start μApp2**

To launch dashboards:
- **Start Per UE metrics dashboard** OR
- **Start aggreagate statistics dashboard**
