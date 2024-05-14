We are training a PPO agent with the objective of throughput maximization in this particular study.

## Usage

```bash
sudo python3 muApp2_train_RL_DL_scheduling.py --config-name=edge_ric
```

## muApp2_train_RL_DL_scheduling.py

* Trains PPO agent for ```num_iters``` number of iterations
    * One iteration consists of training on 2048 samples and evaluating for 2048 timesteps
    * The evaluation metric (avg reward per episode) is plotted as the training grap


## Repo Structure
```bash

├── conf
│   ├── edge_ric.yaml   # Config file for edgeric RL training
│   ├── example.yaml
│   ├── simpler_streaming.yaml
│   └── single_agent.yaml
├── outputs # Output logs of each training sorted chronologically
│   ├── 2022-10-07
         ├── model_best.pt # Saved policy neural network weights
│          .
│          .
│          .
│          
└── ../stream_rl # Name of the python package implementing the simulator mechanisms
    ├── callbacks.py
    ├── envs # All the envs
    │   ├── cqi_traces
    │   │   ├── data.csv # CQI trace to be used by simulation env
    │   │   └── trace_generator.py # Code to generate synthetic CQI traces
    │   ├── edge_ric.py # Our Env 
    │   ├── simpler_streaming_env.py
    │   ├── single_agent_env.py
    │   └── streaming_env.py
    │   └── __init__.py
    ├── __init__.py
    ├── plots.py # All plotting code
    ├── policy_net # Custom policy net architectures (not currently used)
    │   ├── conv_policy.py
    │   ├── __init__.py
    ├── registry # Registry system for registering envs and rewards (to keep things modular)
    │   └── __init__.py
    └── rewards.py # Definition of reward functions to be used in envs
```
Once the training completes: takes the model_best.pt and save in the ../rl_model folder

## EdgeRIC Env

```
                    CQI1          BL1
                ┌────────────┬─┬─┬─┬─┐
Bernoulli  ───► │            │ │ │ │ │ ──►   f(CQI1,allocated_RGB1)
                │            │ │ │ │ │
                └────────────┴─┴─┴─┴─┘
                    CQI2          BL2
                ┌────────────────┬─┬─┐
Bernoulli  ───► │                │ │ │ ──►   f(CQI2,allocated_RGB2)
                │                │ │ │
                └────────────────┴─┴─┘
                          .
                          .
                          .
                          . num_UEs
                          .
                          .
                          .
                ┌────────────┬─┬─┬─┬─┐
Bernoulli  ───► │            │ │ │ │ │ ──►   f(CQI_N,allocated_RBG_N)
                │            │ │ │ │ │
                └────────────┴─┴─┴─┴─┘
```


* State_space : ```[BL1,CQI1,BL2,CQI2.....]``` (if augmented_state_space=False)
* Action_space : ```[Weight1,Weight2.....]```
* Parameters of the env configurable in ```"./conf/edge_ric.yml"```, under ```env_config``` field

