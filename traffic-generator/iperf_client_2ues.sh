echo "iperf -c 172.16.0.2 -u -i 1 -b $1 -t $3"
iperf -c 172.16.0.2 -u -i 1 -b $1 -t $3  &


sleep 3

echo "iperf -c 172.16.0.3 -u -i 1 -b $2 -t $3"
iperf -c 172.16.0.3 -u -i 1 -b $2 -t $3 
