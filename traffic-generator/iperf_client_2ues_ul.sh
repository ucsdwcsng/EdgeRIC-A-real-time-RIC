echo "sudo ip netns exec ue1 iperf -c 172.16.0.1 -u -i 1 -b $1 -t $3"
sudo ip netns exec ue1 iperf -c 172.16.0.1 -u -i 1 -b $1 -t $3  &


sleep 3

echo "sudo ip netns exec ue2 iperf -c 172.16.0.1 -u -i 1 -b $2 -t $3"
sudo ip netns exec ue2 iperf -c 172.16.0.1 -u -i 1 -b $2 -t $3 
