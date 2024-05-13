# Simulator for RL agent training

## Usage - EdgeRIC architecture

edgeric_agent.py
    get_metrics()
    send_control() - only once all microapps finish - [TODO] incorporate restrictions: all apps must complete
    conflict management/ acts based on number of microapps, else sends default numbers

Microapps:
    edgeric_run_scheduling.py
    edgeric_blank_prbs.py
    edgeric_trainRL_ppo.py - uses emulator module - tiny twin to train in cloud - drops trained models - redis

## What we support:
Per UE KPI recieved from RAN - UEs are identified with their KPIs:

  ue_data[rnti] = {
                'CQI': cqi,
                'Downlink Backlog Buffer': backlog,
                'Uplink SNR': snr,
                'Uplink Pending Data': pending_data,
                'Downlink Bitrate' : txb
            }

Message structure from RAN: ue_data + RIC ID + RAN ID

Control message format 
    to support downlink scheduling:
    to support uplink RB blanking:

## Realtime Metrics monitoring
Per UE live metrics
Aggregate Metrics

## How to Run microapps


### downlink scheduling


### uplink PRB blanking
