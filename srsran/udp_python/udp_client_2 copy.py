import socket
from threading import Thread
import time
import sys
import zmq

cur_buff = 0
num_of_stalls = 0
recved = False
kill = False


context_mbuff = zmq.Context()
socket_mbuff = context_mbuff.socket(zmq.PUB)
#port_mbuff = "5559"
port_mbuff = "5566"
socket_mbuff.bind("tcp://*:%s" % port_mbuff)


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
socket_tti.connect("ipc:///tmp/socket_tti")
topicfilter_tti = b""
socket_tti.setsockopt(zmq.SUBSCRIBE, b"")


def thread_recv():
	global cur_buff, recved, kill
	msgFromClient = "Hello UDP Server"
	bytesToSend = str.encode(msgFromClient)
	serverAddressPort = ("172.16.0.1",50002)
	#serverAddressPort = ("127.0.0.1",20001)
	bufferSize = 1024

	UDPClientSocket = socket.socket(family = socket.AF_INET, type = socket.SOCK_DGRAM)
	UDPClientSocket.sendto(bytesToSend, serverAddressPort)
	max_buff = 1000000

	while not kill:
		msgFromServer = UDPClientSocket.recvfrom(bufferSize)
		recved = True
		sz = len(msgFromServer[0])
		cur_buff = cur_buff+sz
		if cur_buff > max_buff:
			cur_buff = max_buff
		#print(cur_buff)
	sys.exit(1)
		
def thread_play():
	global cur_buff, num_of_stalls, recved, kill
	
	#sz_frame = int(2*512*1024/freq)
	f_params = open("params_app_2.txt")	
	idx_client = 1
	line_rate = 0
	line_freq = 1
	
	lines = f_params.readlines()
	sz_bulk= int(lines[line_rate].split()[idx_client])
	sz_frame = sz_bulk*1024

	print("sz_bulk [Kbytes]:", sz_bulk)
	
	# playing rate: 512KB/sec
	freq = 1/float(lines[line_freq].split()[idx_client])
	print("freq:", freq)
	#freq = 60
	######
	
	
	#sz_frame = int(run_rate*1024*1024*1.0/8/freq)
	
	count  = 0
	filename  = "build/out_client2.txt"
	f = open(filename, "w")
	
	
	interval_play = 1.0/freq
	print("interval_play", interval_play)
	while not kill:
		#print("before", cur_buff, num_of_stalls, sz_frame)
		cur_buff = cur_buff - sz_frame
		

		if cur_buff < 0 and recved == True:
			num_of_stalls = num_of_stalls +1
			#print(num_of_stalls)
		
		if cur_buff < 0: cur_buff = 0

		topic_mbuff = "mbuff2"
		str_to_send = ""
        	
		#str_to_send =  topic_mbuff + " " + str(cur_buff)+ " " + str(num_of_stalls)
		str_to_send =  str(cur_buff)
		
		tti = ""
		#socket_mbuff.send(b"%s %s " % (topic_mbuff, str(cur_buff)))
		try: 
			tti = socket_tti.recv(flags=zmq.NOBLOCK)
			#print("recved", tti)
		except Exception as e:
			#print("none")
			tti = ""
		#print("len(tti)", len(tti))

		
		if len(tti) >= 0 :
			socket_mbuff.send_string(str_to_send)

		'''
		# for request
		threshod = 1000000*0.05
		#if (cur_buff <= threshod and flag_request is False):
		if (cur_buff <= threshod):
			msgFromClient = "request"
			bytesToSend = str.encode(msgFromClient)
			serverAddressPort = ("172.16.0.1",50002)
			#serverAddressPort = ("127.0.0.1",20001)
			

			UDPClientSocket = socket.socket(family = socket.AF_INET, type = socket.SOCK_DGRAM)
			UDPClientSocket.sendto(bytesToSend, serverAddressPort)
			#print("sent a request", cur_buff, threshod)
			flag_request = True
		'''

		log = str(time.time()) + ", " + str(cur_buff) + ", " + str(num_of_stalls)+ "\r"
		f.write(log)
		
		if count == 1000 : 
			#print(time.time(), cur_buff, num_of_stalls, sz_frame)
				
			count = 0
		
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
				print("\n",reset, "\n")
				cur_buff = 5120
				num_of_stalls = 0 
				recved = False
		except Exception as e:
			reset = ""			
		#print(buffer)
	sys.exit(1)

def main():
	global cur_buff, num_of_stalls, kill, recved
	t_recv = Thread(target = thread_recv)
	t_play = Thread(target = thread_play)
	t_reset = Thread(target = thread_reset)
	
	t_recv.start()
	t_play.start()
	t_reset.start()
	
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
		print("Thread successfully closed 0")
		time.sleep(0.5)
		sys.exit(1)
		
	
if __name__=='__main__':
	main()


	

