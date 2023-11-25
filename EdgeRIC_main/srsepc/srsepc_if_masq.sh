#!/bin/bash

#
# Copyright 2013-2022 Software Radio Systems Limited
#
# This file is part of srsRAN
#
# srsRAN is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of
# the License, or (at your option) any later version.
#
# srsRAN is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# A copy of the GNU Affero General Public License can be found in
# the LICENSE file in the top-level directory of this distribution
# and at http://www.gnu.org/licenses/.
#

#Check for sudo rights
sudo -v || exit 

#Check if outbound interface was specified
if [ ! $# -eq 1 ]
  then
    echo "Usage :'sudo ./srsepc_if_masq.sh <Interface Name>' "
    exit
fi

echo "Masquerading Interface "$1

echo 1 | sudo tee /proc/sys/net/ipv4/ip_forward 1 >/dev/null
sudo iptables -A FORWARD -o eno1 -i srs_spgw_sgi -j ACCEPT
sudo iptables -A FORWARD -i eno1 -o srs_spgw_sgi -j ACCEPT
#sudo iptables -t nat -A POSTROUTING -o $1 -j MASQUERADE


#sudo ip tuntap add dev tun1 mode tun user `id -un`
#sudo ip link set dev tun1 up
#sudo ip addr add dev srs_spgw_sgi local 172.16.0.0 remote 172.16.0.1
#sudo iptables -t filter -I FORWARD -i srs_spgw_sgi -o eno1 -j ACCEPT
#sudo iptables -t filter -I FORWARD -m state --state ESTABLISHED,RELATED -j ACCEPT
#sudo iptables -t nat -I POSTROUTING -o eno1 -j MASQUERADE
sudo sysctl net.ipv4.ip_forward=1
#/path/to/your/packet/generator/program tun1
