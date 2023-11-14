import zmq
import time 
context = zmq.Context()
socket = context.socket(zmq.SUB)
port = "5557" # port 
socket.connect("tcp://localhost:%s" % port)

topicfilter = "metrics"

socket.setsockopt(zmq.SUBSCRIBE, topicfilter)



context_mbuff = zmq.Context()
socket_mbuff = context_mbuff.socket(zmq.SUB)
ip_ue = "172.16.0.2"
port_mbuff = "5558" # port 
socket_mbuff.connect("tcp://%s:%s" % (ip_ue, port_mbuff))


topicfilter_mbuff = "mbuff"
socket_mbuff.setsockopt(zmq.SUBSCRIBE, topicfilter_mbuff)

# parameters to be determined
num_of_ues = 1
num_of_params = 3
##

cqi_avg = [0.0]*num_of_ues 
cnt = 0
window = 1000
weights= [0.0]*num_of_ues


stored_cqi= {}


try:
	while True:
		#
		#print string
		string_mbuff= ""
		string=""
		try:
			string = socket.recv(flags=zmq.NOBLOCK)
			string_mbuff = socket_mbuff.recv(flags=zmq.NOBLOCK)
			#string_mbuff = socket_mbuff.recv()
		except zmq.ZMQError as e:
			if e.errno == zmq.EAGAIN:
				pass
			else :
				traceback.print_exec()	

		
		#print string
		#print "\t\t\t\t", string_mbuff

		time.sleep(0.001)
		
		messagedata = string.split()
		
		if (len(messagedata) > 0):
			print "metrics: "
			rnti = [0]*num_of_ues
			tx_brate = [0.0]*num_of_ues
			dl_cqi = [0.0]*num_of_ues
			
			for i_ue in range(0,num_of_ues):
				idx = i_ue*num_of_params
				
				## Get rnti	
				rnti[i_ue] = int(messagedata[1+idx])
				
				## Get tx_brate
				tx_brate[i_ue] = float(messagedata[2+idx])
				

				## Get cqi
				dl_cqi[i_ue] = int(messagedata[3+idx])
				if dl_cqi[i_ue] > 0: 
					stored_cqi[str(rnti[i_ue])] = str(dl_cqi[i_ue])
				else:
					if stored_cqi.has_key(str(rnti[i_ue])):
						dl_cqi[i_ue] = int(stored_cqi[str(rnti[i_ue])])
					
				print "ue",i_ue,"rnti: ", rnti[i_ue], " brate: ", tx_brate[i_ue] , "cqi: ", dl_cqi[i_ue]
		
		messagedata_mbuff = string_mbuff.split()
		if (len(messagedata_mbuff) > 0):
			media_buffer = int(messagedata_mbuff[1])
			print "\n\n\t\t\t\t\t","media buffer: ", media_buffer, "\n"
		

except KeyboardInterrupt:
	print("stopped")
