# echo "cd build/"
cd build/

echo "srsepc ../.config/srsran/epc.conf"
srsepc ../.config/srsran/epc.conf  &

sleep 1

echo "./srsenb/src/srsenb /home/santosh/.config/srsran/enb.conf --rf.device_name=zmq --rf.device_args=fail_on_disconnect=true,tx_port=tcp://*:2101,rx_port=tcp://localhost:2100,id=enb,base_srate=23.04e6"
./srsenb/src/srsenb ../.config/srsran/enb.conf --rf.device_name=zmq --rf.device_args="fail_on_disconnect=true,tx_port=tcp://*:2101,rx_port=tcp://localhost:2100,id=enb,base_srate=23.04e6"  &

sleep 1

echo "./srsue/src/srsue ../.config/srsran/ue.conf --rf.device_name=zmq --rf.device_args=tx_port=tcp://*:2001,rx_port=tcp://localhost:2000,id=ue,base_srate=23.04e6 --gw.netns=ue1 --params_filename=../params1.txt"

./srsue/src/srsue ../.config/srsran/ue.conf --rf.device_name=zmq --rf.device_args="tx_port=tcp://*:2001,rx_port=tcp://localhost:2000,id=ue,base_srate=23.04e6" --gw.netns=ue1 --params_filename="../params1.txt" &


sleep 1

echo "./srsue/src/srsue2 ../.config/srsran/ue2.conf --rf.device_name=zmq --rf.device_args=tx_port=tcp://*:2011,rx_port=tcp://localhost:2010,id=ue,base_srate=23.04e6 --gw.netns=ue2 --params_filename=../params2.txt"

./srsue/src/srsue2 ../.config/srsran/ue2.conf --rf.device_name=zmq --rf.device_args="tx_port=tcp://*:2011,rx_port=tcp://localhost:2010,id=ue,base_srate=23.04e6" --gw.netns=ue2 --params_filename="../params2.txt"



