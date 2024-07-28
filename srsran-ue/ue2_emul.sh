# echo "cd build/"

#cd ../srsran_ue2/build
cd build/

echo "./srsue/src/srsue2 ../.config/srsran/ue2.conf --rf.device_name=zmq --rf.device_args=tx_port=tcp://*:2011,rx_port=tcp://localhost:2010,id=ue,base_srate=23.04e6 --gw.netns=ue2 --params_filename=../params2.txt"

./srsue/src/srsue2 ../.config/srsran/ue2.conf --rf.device_name=zmq --rf.device_args="tx_port=tcp://*:2011,rx_port=tcp://localhost:2010,id=ue,base_srate=23.04e6" --gw.netns=ue2 --params_filename="../params2.txt"
