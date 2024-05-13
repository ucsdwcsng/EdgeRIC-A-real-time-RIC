# Simulator for RL agent training

## RT-E2 agent

edgeric_agent.py
    get_metrics()
    send_control() - only once all microapps finish - [TODO] incorporate restrictions: all apps must complete
    conflict management/ acts based on number of microapps, else sends default numbers

Microapps:
    edgeric_run_scheduling.py
    edgeric_blank_prbs.py
    edgeric_trainRL_ppo.py - uses emulator module - tiny twin to train in cloud - drops trained models - redis

## How to launch the EdgeRIC controller gui
'''bash
sudo python3 controller_gui.py
'''

## MicroApps supported
