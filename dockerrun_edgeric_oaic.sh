#!/bin/bash

#export DISPLAY=:93
xhost +local:docker

#xhost +local:docker

systemctl stop firewalld

sysctl -w net.ipv4.ip_forward=1


docker build -t edgeric_base_files_oaic -f Dockerfile_EdgeRIC_run_oaic .

docker run -it --rm --network=$1 --name edgeric_$2 --privileged=true -e DISPLAY=$DISPLAY --env=NVIDIA_DRIVER_CAPABILITiES=all --env=NVIDIA-VISIBLE_DEVICES=all --env=QT_X11_NO_MITSHM=1 -v $(pwd):/home/EdgeRIC-A-real-time-RIC:rw -v /tmp/.X11-unix:/tmp/.X11-unix:rw -v /dev:/dev edgeric_base_files_oaic bash
 



