## Running Downlink iperf traffic

Terminal 1:  
```bash
./iperf_server_{i}ues.sh
```
Terminal 2:  
```bash
./iperf_client_{i}ues.sh <rate_ue{i}> <duration>, eg: ./iperf_client_2ues.sh 10M 10M 1000
```

## Running Uplink iperf traffic
Terminal 1:  
```bash
./iperf_server_{i}ues_ul.sh
```
Terminal 2:  
```bash
./iperf_client_{i}ues_ul.sh <rate_ue{i}> <duration>, eg: ./iperf_client_2ues.sh 10M 10M 1000
```


## Running various other kinds of Downlink Traffic profiles
Start the servers
```bash
sudo ip netns exec ue1 python3 server.py --host 172.16.0.2 --port 12345
sudo ip netns exec ue2 python3 server.py --host 172.16.0.3 --port 12345
sudo ip netns exec ue3 python3 server.py --host 172.16.0.4 --port 12345
sudo ip netns exec ue4 python3 server.py --host 172.16.0.5 --port 12345
```
Start the clients
```bash
sudo python3 client_embb.py --host 172.16.0.2 --port 12345  #--burst 250000 --min-interval 0.5 --max-interval 2.0
sudo python3 client_urllc.py --host 172.16.0.3 --port 12345
sudo python3 client_xr.py --host 172.16.0.4 --port 12345
sudo python3 client_mmtc.py --host 172.16.0.5 --port 12345
```
