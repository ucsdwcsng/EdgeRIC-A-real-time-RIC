xhost +local:docker

sudo sysctl -w net.ipv4.ip_forward=1


docker build -t uhd_srsran_packages -f Dockerfile_srsran_packages .

