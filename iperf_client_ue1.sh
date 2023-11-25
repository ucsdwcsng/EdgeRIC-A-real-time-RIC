echo "iperf -c 172.16.0.2 -i 1 -b $1 -t $2"
iperf -c 172.16.0.2 -i 1 -t $1 -b $2
