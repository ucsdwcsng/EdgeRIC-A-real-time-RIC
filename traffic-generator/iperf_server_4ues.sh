echo "sudo ip netns exec ue1 iperf -s -u"
sudo ip netns exec ue1 iperf -s -u &



echo "sudo ip netns exec ue2 iperf -s -u"
sudo ip netns exec ue2 iperf -s -u &


echo "sudo ip netns exec ue3 iperf -s -u"
sudo ip netns exec ue3 iperf -s -u &


echo "sudo ip netns exec ue4 iperf -s -u"
sudo ip netns exec ue4 iperf -s -u