#echo "cd srsepc/"
#cd srsepc/

# echo "cd build/"
# cd build/

# echo "sudo srsepc ../.config/epc.conf"
# sudo srsepc ../.config/epc.conf  &

# sleep 5

# echo "sudo ./srsenb/src/srsenb ../.config/enb.conf"
# sudo ./srsenb/src/srsenb ../.config/enb.conf  &

# sleep 5
cd srsRAN_4G/build

echo "sudo ./srsue/src/srsue ../.config/ue1.conf --rf.device_name=zmq --rf.device_args=tx_port=tcp://*:2001,rx_port=tcp://localhost:2000,id=ue,base_srate=23.04e6 --gw.netns=ue1"
sudo ./srsue/src/srsue ../.config/ue1.conf --rf.device_name=zmq --rf.device_args="tx_port=tcp://*:2001,rx_port=tcp://localhost:2000,id=ue,base_srate=23.04e6" --gw.netns=ue1 &

#echo "sudo ./srsue/src/srsue home/wcsng-24/Ushasi/EdgeRIC_main/.config/srsran/ue.conf --rf.device_name=zmq --rf.device_args=tx_port=tcp://*:2001,rx_port=tcp://localhost:2000,id=ue,base_srate=23.04e6 --gw.netns=ue1"
#sudo ./srsue/src/srsue home/wcsng-24/Ushasi/EdgeRIC_main/.config/srsran/ue.conf --rf.device_name=zmq --rf.device_args="tx_port=tcp://*:2001,rx_port=tcp://localhost:2000,id=ue,base_srate=23.04e6" --gw.netns=ue1 &

sleep 2

#cd ../../srsRAN-e2_ue2/build


echo "sudo ./srsue/src/srsue ../.config/ue2.conf --rf.device_name=zmq --rf.device_args=tx_port=tcp://*:2011,rx_port=tcp://localhost:2010,id=ue,base_srate=23.04e6 --gw.netns=ue2"
sudo ./srsue/src/srsue ../.config/ue2.conf --rf.device_name=zmq --rf.device_args="tx_port=tcp://*:2011,rx_port=tcp://localhost:2010,id=ue,base_srate=23.04e6" --gw.netns=ue2 &

sleep 2

#cd ../../srsRAN-e2_ue3/build


echo "sudo ./srsue/src/srsue ../.config/ue3.conf --rf.device_name=zmq --rf.device_args=tx_port=tcp://*:2021,rx_port=tcp://localhost:2020,id=ue,base_srate=23.04e6 --gw.netns=ue3"
sudo ./srsue/src/srsue ../.config/ue3.conf --rf.device_name=zmq --rf.device_args="tx_port=tcp://*:2021,rx_port=tcp://localhost:2020,id=ue,base_srate=23.04e6" --gw.netns=ue3 &

sleep 2

#cd ../../srsRAN-e2_ue4/build


echo "sudo ./srsue/src/srsue ../.config/ue4.conf --rf.device_name=zmq --rf.device_args=tx_port=tcp://*:2031,rx_port=tcp://localhost:2030,id=ue,base_srate=23.04e6 --gw.netns=ue4"
sudo ./srsue/src/srsue ../.config/ue4.conf --rf.device_name=zmq --rf.device_args="tx_port=tcp://*:2031,rx_port=tcp://localhost:2030,id=ue,base_srate=23.04e6" --gw.netns=ue4 
