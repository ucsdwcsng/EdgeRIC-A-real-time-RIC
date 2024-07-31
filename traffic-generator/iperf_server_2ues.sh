echo "sudo ip netns exec ue1 iperf -s -u"
ip netns exec ue1 iperf -s -u &



echo "sudo ip netns exec ue2 iperf -s -u"
ip netns exec ue2 iperf -s -u
