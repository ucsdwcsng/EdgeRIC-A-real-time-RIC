# run RL

echo "cd examples"
cd examples

echo "python3 ppo_gym_multi.py --num-arms"  $1 
sudo python3 ppo_gym_multi.py --num-arms $1

