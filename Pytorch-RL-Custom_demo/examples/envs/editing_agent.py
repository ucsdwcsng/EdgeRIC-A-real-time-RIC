import zmq
import time 
import sys
from threading import Thread



f_ric = open("02112023_rtts_s/log_ric_100ue_s.txt","r")
f_ric_out = open("02112023_rtts_s/100ue/log_ric.txt","w")

lines = f_ric.readlines()
for line in lines:
    line = line.replace("'\"","")
    f_ric_out.write(line)

f_ric.close()
f_ric_out.close()
