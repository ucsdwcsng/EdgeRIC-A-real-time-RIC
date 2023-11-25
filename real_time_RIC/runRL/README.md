# Simulator for RL agent training

## Usage

```bash
python ppo_train.py --config-name=edge_ric
```

## ppo_train.py

* Trains PPO agent for ```num_iters``` number of iterations
    * One iteration consists of training on 2048 samples and evaluating for 2048 timesteps
    * The evaluation metric (avg reward per episode) is plotted as the training graph
* Compares the performance of trained agent against baseline agents (MaxCQI and MaxBackPressure) on ```num_eval_episodes``` number of episodes and plots the reward attained for each agent in each of these eval episodes.


## Repo Structure
```bash
simulator
├── conf
│   ├── edge_ric.yaml   # Config file for edgeric RL training
│   ├── example.yaml
│   ├── simpler_streaming.yaml
│   └── single_agent.yaml
├── model_best.pt # Saved policy neural network weights
├── model_usage.py # File explaining how to use a trained model
├── outputs # Output logs of each training sorted chronologically
│   ├── 2022-10-07
│          .
│          .
│          .
│          
├── ppo_train.py # Main training and evaluation code
├── README.md
├── rllib_train.py # For ray rllib training (not currently used)
└── stream_rl # Name of the python package implementing the simulator mechanisms
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

