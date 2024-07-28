import socket
from threading import Thread
import time
import sys
import zmq


### things to change after copying
##   f_params = open("params_app_1.txt")	
##   filename  = "build/out_client1.txt"


cur_buff = 0
num_of_stalls = 0
recved = False
kill = False



### read parameters
f_params = open("params_app_1.txt")	
idx_server = 0
idx_client = 1
line_rate = 0
line_interval = 1
line_port = 2
line_port_mbuff = 3

lines = f_params.readlines()
sz_bulk= int(lines[line_rate].split()[idx_client])
sz_recvbulk = int(lines[line_rate].split()[idx_server])



print("sz_bulk [Kbytes]:", sz_bulk)

interval_bulk = float(lines[line_interval].split()[idx_server])
print("interval_bulk:", interval_bulk)

# playing rate: 512KB/sec
interval_play = float(lines[line_interval].split()[idx_client])
print("interval_play:", interval_play)
#freq = 60
######


localPort = int(lines[line_port].split()[0])
print("localPort:",localPort )



#port_mbuff = int(lines[line_port_mbuff].split()[0])
port_mbuff = lines[line_port_mbuff].split()[0]
print("port_mbuff:",port_mbuff )

####


serverAddressPort = ("172.16.0.1",localPort)
UDPClientSocket = socket.socket(family = socket.AF_INET, type = socket.SOCK_DGRAM)


context_mbuff = zmq.Context()
socket_mbuff = context_mbuff.socket(zmq.PUB)
#port_mbuff = "5558"
##port_mbuff = "5556" in param.txt
##socket_mbuff.bind("tcp://*:%s" % port_mbuff)
socket_mbuff.bind("%s" % port_mbuff)


# for receiving a reset signal from the RL
context_reset = zmq.Context()
socket_reset = context_reset.socket(zmq.SUB)
####port_RL = "5560"
####socket_reset.connect("tcp://172.16.0.1:%s" % port_RL)
#socket_reset.connect("tcp://127.0.0.1:%s" % port_RL)
socket_reset.connect("ipc:///tmp/socket_reset")
topicfilter_reset = b"reset"
socket_reset.setsockopt(zmq.SUBSCRIBE, topicfilter_reset)

context_tti = zmq.Context()
socket_tti = context_reset.socket(zmq.SUB)
##"ipc:///tmp/socket_metrics"); 
##socket_tti.connect("ipc:///tmp/socket_tti")
socket_tti.connect("ipc:///tmp/socket_metrics")
topicfilter_tti = b""
socket_tti.setsockopt(zmq.SUBSCRIBE, b"")



def thread_recv():
	global cur_buff, recved, kill, serverAddressPort, UDPClientSocket , flag_request
	msgFromClient = "Hello UDP Server"
	bytesToSend = str.encode(msgFromClient)
	
	#serverAddressPort = ("127.0.0.1",20001)
	bufferSize = 1024
	
	
	UDPClientSocket.sendto(bytesToSend, serverAddressPort) 
	max_buff = 1000000
	cnt_recv = 0

	while not kill:
		#print("before")
		msgFromServer = UDPClientSocket.recvfrom(bufferSize)
		recved = True
		sz = len(msgFromServer[0])

		if (flag_request or interval_bulk > 0):
			cur_buff = cur_buff+sz
			if cur_buff > max_buff:
				cur_buff = max_buff
		
		
		cnt_recv = cnt_recv + 1
		#print(time.time(), "cnt_recv " ,cnt_recv, 'sz', sz)

		if (cnt_recv == sz_recvbulk):
			print(time.time(), "recved " ,sz*cnt_recv)
			flag_request = False
			cnt_recv = 0
			


	sys.exit(1)
		
def thread_play():
	global cur_buff, num_of_stalls, recved, kill, sz_bulk, interval_play ,serverAddressPort, UDPClientSocket, flag_request
	
	#sz_frame = int(2*512*1024/freq)
	
	
	sz_frame = sz_bulk*1024
	#sz_frame = int(run_rate*1024*1024*1.0/8/freq)
	
	count = 0
	filename  = "out_client1.txt"
	f = open(filename, "w")
	
	flag_request = False
	while not kill:
		##print("before", cur_buff, num_of_stalls, sz_frame)
		cur_buff = cur_buff - sz_frame
		if cur_buff < 0 and recved == True:
			num_of_stalls = num_of_stalls +1
			#print(num_of_stalls)
		
		if cur_buff < 0: cur_buff = 0
		
		
		
		# for request
		max_buf = 9*1024*1024
		#threshod = max_buf*2/3
		threshod = sz_recvbulk*1024/50

		if (cur_buff <= threshod and flag_request is False and interval_bulk ==0 ):
		#if (cur_buff <= threshod):
			msgFromClient = "request"
			bytesToSend = str.encode(msgFromClient)
			
			
			######serverAddressPort = ("172.16.0.1",50000)
			#serverAddressPort = ("127.0.0.1",20001)
			

			#####UDPClientSocket = socket.socket(family = socket.AF_INET, type = socket.SOCK_DGRAM)
			UDPClientSocket.sendto(bytesToSend, serverAddressPort)
			
			print("\n\nsent a request", cur_buff, threshod)
			flag_request = True
			count = 0
		
		
		log = str(time.time()) + ", " + str(cur_buff) + ", " + str(num_of_stalls) + "\r"
		f.write(log)
		
		#print("log", log)
		if count == 200 : 
			flag_request = False 
			##print(time.time(), cur_buff, num_of_stalls, sz_frame)	
			count = 0
		


		if flag_request :
			count = count + 1

		time.sleep(interval_play)
	
	f.close()
	sys.exit(1)

def thread_reset():
	global cur_buff, num_of_stalls, kill

 	
	while not kill:
		try: 
			reset = socket_reset.recv(flags=zmq.NOBLOCK)
			time.sleep(0.001)
			sz = len(reset)
			if sz > 0 :
				print("\n", reset, "\n")
				cur_buff = 5120
				num_of_stalls = 0 
				recved = False
		except Exception as e:
			reset = ""			
		#print(buffer)
	sys.exit(1)


def thread_tti():
	global cur_buff, num_of_stalls, kill, serverAddressPort, UDPClientSocket

	tti_cnt = 0

	while not kill:
			
		tti = ""
		#socket_mbuff.send(b"%s %s " % (topic_mbuff, str(cur_buff)))
		try:
			####print("waiting") 
			tti = socket_tti.recv()
			###print("recved")
		except Exception as e:
			#print("none")
			tti = ""
		#print("len(tti)", len(tti))
		
		if len(tti) >= 0 :

			###topic_mbuff = "mbuff1"
			###print("sending", cur_buff)
			## send the current media buffer size to RIC 
			socket_mbuff.send_string(str(cur_buff))



			'''
			## send a request to the UDP server every tti
			msgFromClient = "request"
			bytesToSend = str.encode(msgFromClient)
			
			#serverAddressPort = ("127.0.0.1",20001)
			
			UDPClientSocket.sendto(bytesToSend, serverAddressPort)
			##print("sent a request")
			##flag_request = True
			'''

			
	sys.exit(1)

def main():
	global cur_buff, num_of_stalls, kill, recved, flag_request
	t_recv = Thread(target = thread_recv)
	t_play = Thread(target = thread_play)
	t_reset = Thread(target = thread_reset)
	t_tti = Thread(target = thread_tti)
	
	t_recv.start()
	t_play.start()
	t_reset.start()
	t_tti.start()
	
	interval_state = 0.01  # [sec]
	#interval_reset = 10 # [sec]
	interval_print = 1 # [sec]
	
	#counting_reset = 0
	counting_print = 0
	t0 = time.time()
	print("time [sec]	cur buff  # of stalls")
	try:
		while True:
			counting_print = counting_print + interval_state
			if counting_print > interval_print:
				print((time.time()-t0), "current buffer state:", cur_buff, "bytes", "# of stalls:", num_of_stalls)
				counting_print = 0
		
			#counting_reset = counting_reset + interval_state
			#if counting_reset  >= interval_reset:
			#	cur_buff = 0
			#	num_of_stalls = 0
			#	counting_reset = 0
			#	recved = False
			
			time.sleep(interval_state)
	except KeyboardInterrupt:
		print("Thread successfully closed 3")
		kill = True
		time.sleep(0.5)
		t_recv.join()
		print("Thread successfully closed 2")		
		time.sleep(0.5)
		t_play.join()
		print("Thread successfully closed 1")		
		time.sleep(0.5)
		t_reset.join()
		print("Thread successfully closed 1")		
		time.sleep(0.5)
		t_tti.join()

		print("Thread successfully closed 0")
		time.sleep(0.5)
		sys.exit(1)
		
	
if __name__=='__main__':
	main()


	

