#xhost +local:docker

#sudo su


systemctl stop firewalld

sysctl -w net.ipv4.ip_forward=1


docker build --no-cache -t edgeric_base -f Dockerfile_EdgeRIC_build .
#docker build -t edgeric_base -f Dockerfile_EdgeRIC_build .

