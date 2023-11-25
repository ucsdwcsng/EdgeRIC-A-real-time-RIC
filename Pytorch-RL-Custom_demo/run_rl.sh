# run RL

echo "cd examples"
cd examples

echo "python3 ppo_gym_multi.py --max-iter"  $1 "--run-tag "$2
python3 ppo_gym_multi.py --max-iter $1 --run-tag $2

