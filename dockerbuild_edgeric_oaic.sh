
#export DISPLAY=:93
xhost +local:docker

systemctl stop firewalld

sysctl -w net.ipv4.ip_forward=1

#docker build --no-cache -t edgeric_base_oaic -f Dockerfile_EdgeRIC_build_oaic .
docker build -t edgeric_base_oaic -f Dockerfile_EdgeRIC_build_oaic .

