#!/bin/bash


xhost +local:docker

docker run -it --rm --network=$1 --name uhd_$2 --privileged --env=DISPLAY --env=NVIDIA_DRIVER_CAPABILITiES=all --env=NVIDIA-VISIBLE_DEVICES=all --env=QT_X11_NO_MITSHM=1 -v /dev:/dev uhd bash
 



