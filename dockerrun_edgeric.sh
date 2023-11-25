#!/bin/bash


xhost +local:docker
#xhost +localhost

systemctl stop firewalld

sysctl -w net.ipv4.ip_forward=1



docker build -t edgeric_base_files -f Dockerfile_EdgeRIC_run .

#docker run -it --rm --network=$1 --device="/dev/video$2:/dev/video$2" --name eware_$3 --privileged --env=DISPLAY --env=NVIDIA_DRIVER_CAPABILITiES=all --env=NVIDIA-VISIBLE_DEVICES=all --env=QT_X11_NO_MITSHM=1 -v /tmp/.X11-unix:/tmp/.X11-unix:rw jackal_eware_base_files bash
#docker run -it --rm --network=$1 --name edgeric_$3 --privileged --env=DISPLAY --env=NVIDIA_DRIVER_CAPABILITiES=all --env=NVIDIA-VISIBLE_DEVICES=all --env=QT_X11_NO_MITSHM=1 -v /tmp/.X11-unix:/tmp/.X11-unix:rw edgeric_base_files bash
#docker run -it --rm --network=$1 --name edgeric_$2 --privileged --env=DISPLAY --env=NVIDIA_DRIVER_CAPABILITiES=all --env=NVIDIA-VISIBLE_DEVICES=all --env=QT_X11_NO_MITSHM=1 -v /tmp/.X11-unix:/tmp/.X11-unix:rw edgeric_base_files bash
# docker run -it --rm --network=$1 --name edgeric_$2 --privileged -e DISPLAY=$DISPLAY --env=NVIDIA_DRIVER_CAPABILITiES=all --env=NVIDIA-VISIBLE_DEVICES=all --env=QT_X11_NO_MITSHM=1 -v /tmp/.X11-unix:/tmp/.X11-unix:rw edgeric_base_files bash
#docker run -it --rm --network=$1 --name edgeric_$2 --privileged=true -e DISPLAY=$DISPLAY --env=NVIDIA_DRIVER_CAPABILITiES=all --env=NVIDIA-VISIBLE_DEVICES=all --env=QT_X11_NO_MITSHM=1 -v /tmp/.X11-unix:/tmp/.X11-unix:rw edgeric_base_files bash
docker run -it --rm --network=$1 --name edgeric_$2 --privileged=true -e DISPLAY=$DISPLAY --env=NVIDIA_DRIVER_CAPABILITiES=all --env=NVIDIA-VISIBLE_DEVICES=all --env=QT_X11_NO_MITSHM=1 -v /tmp/.X11-unix:/tmp/.X11-unix:rw -v /dev:/dev edgeric_base_files bash
 



