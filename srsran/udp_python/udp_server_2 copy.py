
import socket
import time

#localIP = "10.229.167.57"
#localIP = "127.0.0.1"
localIP = "172.16.0.1"
localPort = 50002
bufferSize = 1024

msgFromServer = "Hello UDP Client"
#bytesToSend = str.encode(msgFromServer)

UDPServerSocket = socket.socket(family=socket.AF_INET, type = socket.SOCK_DGRAM)


UDPServerSocket.bind((localIP, localPort))

print("UDP server up and listening")

# runtime of video [sec]
fast_factor= 3
runtime = 6000000 # [sec]

# size of the video [bytes] 	# 512KB/sec * 2 = 10240KB/sec
total_sz= int(512*1024*runtime)

packet_sz= 1024

num_of_packets = int(total_sz/packet_sz)

### params
f_params = open("params_app_2.txt")	
idx_server = 0
line_rate = 0
line_interval = 1

lines = f_params.readlines()
##run_rate= float(lines[line_rate].split()[idx_server])
sz_bulk = int(lines[line_rate].split()[idx_server])

print("sz_bulk [Kbytes]:", sz_bulk)
# interal of sending each bulk [sec]
#interval_bulk = 0.01
interval_bulk = float(lines[line_interval].split()[idx_server])

print("interval:", interval_bulk)
num_of_bulks = int(runtime/fast_factor/interval_bulk)
###
 
#sz_bulk = int(2*512*1024*interval_bulk/packet_sz)  #int(num_of_packets / num_of_bulks)


#sz_bulk = round(run_rate*1024*1024/8*interval_bulk/packet_sz)  #int(num_of_packets / num_of_bulks)

print("bulk size: ", sz_bulk)


t0 = time.time()

while(True):

	bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)
	message = bytesAddressPair[0]
	address = bytesAddressPair[1]
	clientMsg = "Messge from Client:{}".format(message)
	clientIP = "Client IP Address:{}".format(address)
	
	print(clientMsg)
	print(clientIP)


	print("time [sec}	size of sent packets [bytes]")
	#for i in range(num_of_bulks):
	count = 1 
	while(True):
		sz_sent_packets = 0 
		
		for j in range(sz_bulk):
			bytesToSend = bytearray(packet_sz)
			UDPServerSocket.sendto(bytesToSend, address)
			sz_sent_packets = sz_sent_packets + packet_sz
		
		#bytesToSend = bytearray(sz_bulk)
		#UDPServerSocket.sendto(bytesToSend, address)

		if count == int(1.0/interval_bulk): 
			#print(time.time(), sz_sent_packets, len(bytesToSend), sz_bulk)
			print(time.time()-t0, "bytesToSend every", interval_bulk*1000, "msec:", sz_sent_packets, "bytes")
			count =0
		
		count = count + 1
		
			
		# for a fixed rate
		time.sleep(interval_bulk)
		#print("before recv")

		## for request and response
		'''
		bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)
		message = bytesAddressPair[0]
		clientMsg = "Messge from Client:{}".format(message)
		#print("recved", clientMsg)
		'''

