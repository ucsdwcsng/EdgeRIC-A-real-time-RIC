## RT-E2 agent
```bash
edgeric_agent
├── get_metrics_multi()  # get_metrics(): receive metrics from RAN, called by all μApps
│   ├── returnd ue_data dictionaru
├── send_control() # send the RT-E2 policy message to RAN once all μApps complete execution
    ├── send_scheduling_weight() #prepares the control message for the downlink scheduling action
    ├── send_ul_prb() #prepares the control message for the uplikn scheduling action

```

## μApps supported
```bash
├── /muApp1           # weight based abstraction of downlink scheduling control
│   ├── muApp1_run_DL_scheduling.py
├── /muApp2           # training an RL agent to compute downlink scheduling policy
    ├── muApp2_train_RL_DL_scheduling.py
├── /muApp3           # training an RL agent to compute downlink scheduling policy
    ├── metrics_monitor_aggregate.py
    ├── metrics_monitor_perUE.py

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
