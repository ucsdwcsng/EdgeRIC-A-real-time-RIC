echo "sudo python3 client_embb.py --host 172.16.0.2 --port 12345"
sudo python3 client_embb.py --host 172.16.0.2 --port 12345 &

sleep 3

echo "sudo python3 client_urllc.py --host 172.16.0.3 --port 12345"
sudo python3 client_urllc.py --host 172.16.0.3 --port 12345 &

#sleep 3

#echo "sudo python3 client_embb.py --host 172.16.0.4 --port 12345"
#sudo python3 client_embb.py --host 172.16.0.4 --port 12345 &

#sleep 3

#echo "sudo python3 client_embb.py --host 172.16.0.5 --port 12345"
#sudo python3 client_embb.py --host 172.16.0.5 --port 12345 