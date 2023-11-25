
import socket
import time


### things to change after copying
##   f_params = open("params_app_1.txt")	



### params
f_params = open("params_app_2.txt")	
idx_server = 0
line_rate = 0
line_interval = 1
line_port = 2

lines = f_params.readlines()
##run_rate= float(lines[line_rate].split()[idx_server])
sz_bulk = int(lines[line_rate].split()[idx_server])
print("sz_bulk [Kbytes]:", sz_bulk)

# interal of sending each bulk [sec]
#interval_bulk = 0.01
interval_bulk = float(lines[line_interval].split()[idx_server])
print("interval:", interval_bulk)


localPort = int(lines[line_port].split()[idx_server])
print("localPort:",localPort )

#localIP = "10.229.167.57"
#localIP = "127.0.0.1"
localIP = "172.16.0.1"
#localPort = 50000

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

	count = 1
	tti_cnt = 0 

	t_prev = time.time()
	
	while(True):
		sz_sent_packets = 0 
		#print (sz_bulk*packet_sz)
				
		# for a periodic transmission
		
		t0 = time.time()
		for j in range(sz_bulk):
			bytesToSend = bytearray(packet_sz)
			UDPServerSocket.sendto(bytesToSend, address)
			sz_sent_packets = sz_sent_packets + packet_sz
			time.sleep(0.001)
		
		#bytesToSend = bytearray(10*packet_sz)
		#UDPServerSocket.sendto(bytesToSend, address)
		print("\n\nsent", sz_sent_packets, j, time.time()-t0)

		if interval_bulk > 0:
			# for a fixed rate
			time.sleep(interval_bulk)
			#print("before recv")
			if count == int(1.0/interval_bulk): 
				#print(time.time(), sz_sent_packets, len(bytesToSend), sz_bulk)
				print(time.time()-t0, "bytesToSend every", 1000, "msec:", sz_sent_packets, "bytes")
				count =0

			##print(time.time(), sz_sent_packets, len(bytesToSend), sz_bulk)
		else :

			## for request and response
			## period of request: 

			
			req_period = 1
			if interval_bulk == 0:

				tti_cnt = 0 			
				while  tti_cnt < req_period: # wait until receiving 10 TTIs
					bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)
					message = bytesAddressPair[0]
					clientMsg = "Messge from Client:{}".format(message)

					tti_cnt = tti_cnt + 1
					###print(time.time(), tti_cnt, count)
		
			
			t_cur = time.time()
			if t_cur- t_prev >= 1: 
				#print(time.time(), sz_sent_packets, len(bytesToSend), sz_bulk)
				print(time.time()-t0, "bytesToSend upon a request ", sz_sent_packets, "bytes")
				count =0
				t_prev = time.time()

			

		count = count + 1

			


