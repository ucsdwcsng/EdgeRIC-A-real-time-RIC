xhost +local:docker

sysctl -w net.ipv4.ip_forward=1


docker build --no-cache -t uhd -f Dockerfile .

