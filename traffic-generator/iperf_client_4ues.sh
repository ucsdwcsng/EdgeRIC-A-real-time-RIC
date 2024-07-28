echo "iperf -c 172.16.0.2 -u -i 1 -b $1 -t $5"
iperf -c 172.16.0.2 -u -i 1 -b $1 -t $5  &


sleep 5

echo "iperf -c 172.16.0.3 -u -i 1 -b $2 -t $5"
iperf -c 172.16.0.3 -u -i 1 -b $2 -t $5 &  

sleep 5

echo "iperf -c 172.16.0.4 -u -i 1 -b $3 -t $5"
iperf -c 172.16.0.4 -u -i 1 -b $3 -t $5 &

sleep 5

echo "iperf -c 172.16.0.5 -u -i 1 -b $4 -t $5"
iperf -c 172.16.0.5 -u -i 1 -b $4 -t $5