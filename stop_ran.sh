#!/bin/bash

# Stop all running srsRAN processes
pkill -9 srsue
pkill -9 srsenb
pkill -9 srsepc
pkill -9 srsue2

# Clear temporary files
rm -rf /dev/shm/srs* /tmp/srs* /var/tmp/srs* /tmp/ue* /tmp/gnb*

# Check for and kill zombie processes
ps aux | grep srs | awk '{print $2}' | xargs kill -9

# Clear Redis cache (if using Redis)
redis-cli FLUSHALL

# Kill any ping processes in the 172.16.0.0/16 network
ps aux | grep 'ping 172.16.0.' | grep -v grep | awk '{print $2}' | xargs kill -9

echo "Cleanup complete."
