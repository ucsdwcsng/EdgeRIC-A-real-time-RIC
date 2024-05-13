## RT-E2 agent
```bash
edgeric_agent
├── get_metrics_multi()  # get_metrics(): receive metrics from RAN, called by all μApps
│   ├── returnd ue_data dictionaru
├── send_control() # send the RT-E2 policy message to RAN once all μApps complete execution
    ├── send_scheduling_weight() #prepares the control message for the downlink scheduling action
    ├── send_ul_prb() #prepares the control message for the uplikn scheduling action

```

## How to launch the EdgeRIC controller gui
```bash
sudo python3 controller_gui.py
```

## μApps supported
```bash
├── /muApp1           # weight based abstraction of downlink scheduling control
│   ├── muApp1_run_DL_scheduling.py
├── /muApp2           # training an RL agent to compute downlink scheduling policy
    ├── muApp2_train_RL_DL_scheduling.py

```
