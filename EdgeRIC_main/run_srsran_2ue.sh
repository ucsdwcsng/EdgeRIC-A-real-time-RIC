#echo "cd srsepc/"
#cd srsepc/

echo "cd build/"
cd build/

echo "sudo srsepc ../.config/srsran/epc.conf"
sudo srsepc ../.config/srsran/epc.conf  &

#sleep 5

#echo "sudo ./srsepc_if_masq.sh eno1"
#sudo ./srsepc_if_masq.sh eno1 &

#sleep 5

#echo "cd .."
#cd .. &

#echo "sudo srsepc"
#sudo srsepc &

#sleep 5

#echo "sudo srsenb"
#sudo srsenb &

sleep 5

#echo "sudo srsepc_if_masq.sh eno1"
#sudo srsepc_if_masq.sh eno1 &
echo "sudo ./srsenb/src/srsenb ../.config/srsran/enb.conf"
sudo ./srsenb/src/srsenb ../.config/srsran/enb.conf  &

sleep 5


#echo "sudo srsepc /home/wcsng-24/Ushasi/EdgeRIC_main/.config/srsran/epc.conf"
#sudo srsepc /home/wcsng-24/Ushasi/EdgeRIC_main/.config/srsran/epc.conf &

#echo "sudo ./srsenb/src/srsenb /home/wcsng-24/Ushasi/EdgeRIC_main/.config/srsran/enb.conf --rf.device_name=zmq --rf.device_args=fail_on_disconnect=true,tx_port=tcp://*:2101,rx_port=tcp://localhost:2100,id=enb,base_srate=23.04e6"
#sudo ./srsenb/src/srsenb home/wcsng-24/Ushasi/EdgeRIC_main/.config/srsran/enb.conf --rf.device_name=zmq --rf.device_args="fail_on_disconnect=true,tx_port=tcp://*:2101,rx_port=tcp://localhost:2100,id=enb,base_srate=23.04e6" &

#echo "sudo ./srsenb/src/srsenb /home/.config/srsran/enb.conf --rf.device_name=zmq --rf.device_args=fail_on_disconnect=true,tx_port=tcp://*:2101,rx_port=tcp://localhost:2100,id=enb,base_srate=23.04e6"
#sudo ./srsenb/src/srsenb ../.config/srsran/enb.conf --rf.device_name=zmq --rf.device_args="fail_on_disconnect=true,tx_port=tcp://*:2101,rx_port=tcp://localhost:2100,id=enb,base_srate=23.04e6"  &

#echo "sudo ./srsenb/src/srsenb /home/wcsng-24/.config/srsran/enb.conf --rf.device_name=zmq --rf.device_args=fail_on_disconnect=true,tx_port=tcp://*:2101,rx_port=tcp://localhost:2100,id=enb,base_srate=23.04e6"
#sudo ./srsenb/src/srsenb /home/wcsng-24/.config/srsran/enb.conf --rf.device_name=zmq --rf.device_args="fail_on_disconnect=true,tx_port=tcp://*:2101,rx_port=tcp://localhost:2100,id=enb,base_srate=23.04e6"  &

#sleep 5

#echo "cd build/"
#cd build/

echo "sudo ./srsue/src/srsue ../.config/srsran/ue.conf --rf.device_name=zmq --rf.device_args=tx_port=tcp://*:2001,rx_port=tcp://localhost:2000,id=ue,base_srate=23.04e6 --gw.netns=ue1"
sudo ./srsue/src/srsue ../.config/srsran/ue.conf --rf.device_name=zmq --rf.device_args="tx_port=tcp://*:2001,rx_port=tcp://localhost:2000,id=ue,base_srate=23.04e6" --gw.netns=ue1 &

#echo "sudo ./srsue/src/srsue home/wcsng-24/Ushasi/EdgeRIC_main/.config/srsran/ue.conf --rf.device_name=zmq --rf.device_args=tx_port=tcp://*:2001,rx_port=tcp://localhost:2000,id=ue,base_srate=23.04e6 --gw.netns=ue1"
#sudo ./srsue/src/srsue home/wcsng-24/Ushasi/EdgeRIC_main/.config/srsran/ue.conf --rf.device_name=zmq --rf.device_args="tx_port=tcp://*:2001,rx_port=tcp://localhost:2000,id=ue,base_srate=23.04e6" --gw.netns=ue1 &

sleep 2

cd ../../EdgeRIC_main_ue2/build


echo "sudo ./srsue/src/srsue ../.config/srsran/ue2.conf --rf.device_name=zmq --rf.device_args=tx_port=tcp://*:2011,rx_port=tcp://localhost:2010,id=ue,base_srate=23.04e6 --gw.netns=ue2"
sudo ./srsue/src/srsue ../.config/srsran/ue2.conf --rf.device_name=zmq --rf.device_args="tx_port=tcp://*:2011,rx_port=tcp://localhost:2010,id=ue,base_srate=23.04e6" --gw.netns=ue2 
