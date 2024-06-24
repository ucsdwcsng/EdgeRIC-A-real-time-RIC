## Usage
```bash
sudo python3 muApp1_run_DL_scheduling.py
```
## Setting the scheduler algorithm manually
Set the scheduling algorithm you want to run:
```bash
# Line 259
selected_algorithm = "Max CQI"   # selection can be: Max CQI, Max Weight,
                                 # Proportional Fair (PF), Round Robin - to be implemneted
                                 # RL - models are included for 2 UEs
```
If the algorithm selected is RL, set the directory for the RL model
```bash
# Line 270
rl_model_name = "Fully Trained Model"  # selection can be Initial Model,
                                       # Half Trained Model, Fully Trained Model - to see benefits, run UE1 with load 5Mbps, UE2 with 21Mbps
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

## Setting the scheduler algorithm with the controller gui - TODO

```bash
sudo python3 controller_gui.py
```
To launch the DL scheduling μApp:
- **Start μApp1** 
  - **Choose the algorithm you want to run**
    - **If traditional:** Choose between Max CQI, Max Weight, PF, Round Robin
    - **If RL:** Specify the directory for the saved RL model [Please Note: the RL scheduler is specific to number of UEs the system started with, refer to the paper]


