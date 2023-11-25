state_delays=(0 20 40 60 80 100)
action_delays=(0 20 40 60 80 100)
for state_delay in ${state_delays[@]}; do
    for action_delay in ${action_delays[@]}; do
        python ppo_gym.py --env-name 'down_link_proto' --state-delay $state_delay --action-delay $action_delay --run-tag "skewed_CQI_state_delayed_${state_delay}_action_delayed_${action_delay}"
    done
done