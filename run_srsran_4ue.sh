cd srsran-ue/build
### commented for now:

echo "./srsue/src/srsue ../../.config/ue1.conf --rf.device_name=zmq --rf.device_args=tx_port=tcp://*:2001,rx_port=tcp://localhost:2000,id=ue,base_srate=23.04e6 --gw.netns=ue1 --params_filename="../params1.txt""
./srsue/src/srsue ../../.config/ue1.conf --rf.device_name=zmq --rf.device_args="tx_port=tcp://*:2001,rx_port=tcp://localhost:2000,id=ue,base_srate=23.04e6" --gw.netns=ue1 --params_filename="../params1.txt" &


sleep 2

#cd ../../srsRAN-e2_ue2/build


echo "./srsue/src/srsue2 ../../.config/ue2.conf --rf.device_name=zmq --rf.device_args=tx_port=tcp://*:2011,rx_port=tcp://localhost:2010,id=ue,base_srate=23.04e6 --gw.netns=ue2 --params_filename="../params2.txt""
./srsue/src/srsue2 ../../.config/ue2.conf --rf.device_name=zmq --rf.device_args="tx_port=tcp://*:2011,rx_port=tcp://localhost:2010,id=ue,base_srate=23.04e6" --gw.netns=ue2 --params_filename="../params2.txt" &

sleep 3

echo "./srsue/src/srsue3 ../../.config/ue3.conf --rf.device_name=zmq --rf.device_args=tx_port=tcp://*:2021,rx_port=tcp://localhost:2020,id=ue,base_srate=23.04e6 --gw.netns=ue3 --params_filename="../params3.txt""
./srsue/src/srsue3 ../../.config/ue3.conf --rf.device_name=zmq --rf.device_args="tx_port=tcp://*:2021,rx_port=tcp://localhost:2020,id=ue,base_srate=23.04e6" --gw.netns=ue3 --params_filename="../params3.txt" &

sleep 3

echo "./srsue/src/srsue4 ../../.config/ue4.conf --rf.device_name=zmq --rf.device_args=tx_port=tcp://*:2031,rx_port=tcp://localhost:2030,id=ue,base_srate=23.04e6 --gw.netns=ue4 --params_filename="../params4.txt""
./srsue/src/srsue4 ../../.config/ue4.conf --rf.device_name=zmq --rf.device_args="tx_port=tcp://*:2031,rx_port=tcp://localhost:2030,id=ue,base_srate=23.04e6" --gw.netns=ue4 --params_filename="../params4.txt" &

sleep 3

#ip netns exec ue1 ping 172.16.0.1 & > /dev/null 2>&1 &
ping 172.16.0.2 > /dev/null 2>&1 &

sleep 3

# ip netns exec ue2 ping 172.16.0.1 > /dev/null 2>&1
ping 172.16.0.3 > /dev/null 2>&1 &

sleep 3

# ip netns exec ue2 ping 172.16.0.1 > /dev/null 2>&1
ping 172.16.0.4 > /dev/null 2>&1 &

sleep 3

# ip netns exec ue2 ping 172.16.0.1 > /dev/null 2>&1
ping 172.16.0.5 > /dev/null 2>&1