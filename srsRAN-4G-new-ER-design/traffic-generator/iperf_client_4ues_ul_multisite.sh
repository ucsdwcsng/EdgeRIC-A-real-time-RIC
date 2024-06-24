echo "sudo ip netns exec ue1 iperf -c 10.45.0.1 -u -i 1 -b $1 -t $5"
sudo ip netns exec ue1 iperf -c 10.45.0.1 -u -i 1 -b $1 -t $5  &


sleep 3

echo "sudo ip netns exec ue2 iperf -c 10.45.0.1 -u -i 1 -b $2 -t $5"
sudo ip netns exec ue2 iperf -c 10.45.0.1 -u -i 1 -b $2 -t $5 &

sleep 3

echo "sudo ip netns exec ue3 iperf -c 10.45.0.1 -u -i 1 -b $3 -t $5"
sudo ip netns exec ue3 iperf -c 10.45.0.1 -u -i 1 -b $3 -t $5 &

sleep 3

echo "sudo ip netns exec ue4 iperf -c 172.16.0.1 -u -i 1 -b $4 -t $5"
sudo ip netns exec ue4 iperf -c 10.45.0.1 -u -i 1 -b $4 -t $5