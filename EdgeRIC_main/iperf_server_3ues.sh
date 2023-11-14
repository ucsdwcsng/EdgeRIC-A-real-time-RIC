echo "sudo ip netns exec ue1 iperf -s"
sudo ip netns exec ue1 iperf -s &



echo "sudo ip netns exec ue2 iperf -s"
sudo ip netns exec ue2 iperf -s &


echo "sudo ip netns exec ue3 iperf -s"
sudo ip netns exec ue3 iperf -s