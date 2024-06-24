# cd srsRAN_4G-ER-ue1/build
# ### commented for now:

# echo "sudo ./srsue/src/srsue ../../srsRAN_4G-ER/.config/ue1.conf --rf.device_name=zmq --rf.device_args=tx_port=tcp://*:2001,rx_port=tcp://localhost:2000,id=ue,base_srate=23.04e6 --gw.netns=ue1"
# sudo ./srsue/src/srsue ../../srsRAN_4G-ER/.config/ue1.conf --rf.device_name=zmq --rf.device_args="tx_port=tcp://*:2001,rx_port=tcp://localhost:2000,id=ue,base_srate=23.04e6" --gw.netns=ue1


# sleep 2

# #cd ../../srsRAN-e2_ue2/build
# cd ../../srsRAN_4G-ER-ue2/build

# echo "sudo ./srsue/src/srsue ../../srsRAN_4G-ER/.config/ue2.conf --rf.device_name=zmq --rf.device_args=tx_port=tcp://*:2011,rx_port=tcp://localhost:2010,id=ue,base_srate=23.04e6 --gw.netns=ue2"
# sudo ./srsue/src/srsue ../../srsRAN_4G-ER/.config/ue2.conf --rf.device_name=zmq --rf.device_args="tx_port=tcp://*:2011,rx_port=tcp://localhost:2010,id=ue,base_srate=23.04e6" --gw.netns=ue2 





cd srsRAN_4G-ER-ue1/build

echo "sudo ./srsue/src/srsue ../../srsRAN_4G-ER/.config/ue1.conf --rf.device_name=zmq --rf.device_args=tx_port=tcp://*:2001,rx_port=tcp://localhost:2000,id=ue,base_srate=23.04e6 --gw.netns=ue1"
sudo ./srsue/src/srsue ../../srsRAN_4G-ER/.config/ue1.conf --rf.device_name=zmq --rf.device_args="tx_port=tcp://*:2001,rx_port=tcp://localhost:2000,id=ue,base_srate=23.04e6" --gw.netns=ue1 &

#echo "sudo ./srsue/src/srsue home/wcsng-24/Ushasi/EdgeRIC_main/.config/srsran/ue.conf --rf.device_name=zmq --rf.device_args=tx_port=tcp://*:2001,rx_port=tcp://localhost:2000,id=ue,base_srate=23.04e6 --gw.netns=ue1"
#sudo ./srsue/src/srsue home/wcsng-24/Ushasi/EdgeRIC_main/.config/srsran/ue.conf --rf.device_name=zmq --rf.device_args="tx_port=tcp://*:2001,rx_port=tcp://localhost:2000,id=ue,base_srate=23.04e6" --gw.netns=ue1 &

sleep 2

cd ../../srsRAN_4G-ER-ue2/build


echo "sudo ./srsue/src/srsue ../../srsRAN_4G-ER/.config/ue2.conf --rf.device_name=zmq --rf.device_args=tx_port=tcp://*:2011,rx_port=tcp://localhost:2010,id=ue,base_srate=23.04e6 --gw.netns=ue2"
sudo ./srsue/src/srsue ../../srsRAN_4G-ER/.config/ue2.conf --rf.device_name=zmq --rf.device_args="tx_port=tcp://*:2011,rx_port=tcp://localhost:2010,id=ue,base_srate=23.04e6" --gw.netns=ue2 
