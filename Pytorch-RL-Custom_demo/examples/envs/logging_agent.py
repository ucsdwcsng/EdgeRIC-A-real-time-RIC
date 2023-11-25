import zmq
import time 
import sys
from threading import Thread
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from random import randrange

## before you import redis you have to install redis on your system by pip install redis
import redis

kill = False

## To connect to a redis server
redis_db = redis.StrictRedis(host = 'localhost', port=6379, decode_responses = False, db=0)
redis_db.flushdb()


fig = plt.figure()
ax1 = fig.add_subplot(1,1,1)
x = [0]
y = [0]
ln , = plt.plot(x,y,'-')

max_y = 40 

plt.axis([0,100,0,max_y])

thrpt = 0


def thread_ran_metrics():
	global kill, redis_db, thrpt ##, flag_request
	

	context = zmq.Context()
	socket = context.socket(zmq.SUB)

	socket.connect("ipc:///tmp/socket_metrics")
	topicfilter = ""

	socket.setsockopt_string(zmq.SUBSCRIBE, topicfilter)
	key_index = 0
	sum= 0 
	x = 0
	#print(time.time(), "thread_ran_metrics: ")
	try:
		while not kill:
			
			string_recved = socket.recv()
			#print(time.time(), "received: ", string_recved)

			# 2. RIC received state information from RAN
			t0 = time.time()
			
			seq_2 = str(t0) + ",\t" + "2"  + ",\t" + str(string_recved)
			
			key_ran = "key_ran_metrics_"+str(key_index)
			## To store data 'seq_2' with a key 'key_ran' in reddis DB
			redis_db.set(key_ran, seq_2) 
			key_index = key_index +1 
			
			data = str(string_recved).split(" ")
			try: 
				tx_byte = int(data[len(data)-2])
				if (key_index % 1000 == 0):
					thrpt = sum/1024.0/1024.0*8 
					print(thrpt)
					
					
					sum = 0
				else:
					sum = sum + tx_byte
			except:
				temp = 1	
			

	except KeyboardInterrupt:
		print("stopped")

	sys.exit(1)



def thread_ric_weights():
	global kill, string_seq_1, redis_db ##, flag_request
	

	context = zmq.Context()
	socket = context.socket(zmq.SUB)

	socket.connect("ipc:///tmp/socket_weights")

	topicfilter = ""

	socket.setsockopt_string(zmq.SUBSCRIBE, topicfilter)
	
	key_index = 0

	try:
		while not kill:
			
			string_recved = socket.recv()
			# 4. RIC transmits weights to RAN
			t0 = time.time()
			seq_4 = str(t0) + ",\t" + "4"   + ",\t" + str(string_recved)
			
			key_ran = "key_ric_weights_"+str(key_index)
			redis_db.set(key_ran, seq_4) # write the frame into the DB 
			key_index = key_index +1 

	except KeyboardInterrupt:
		print("stopped")

	sys.exit(1)

	

def thread_ran_seq():
	global kill, redis_db, key_index_seq ##, flag_request
	

	context = zmq.Context()
	socket = context.socket(zmq.SUB)

	socket.connect("ipc:///tmp/socket_logging_seq")
	topicfilter = ""

	socket.setsockopt_string(zmq.SUBSCRIBE, topicfilter)
	key_index = 0

	try:
		while not kill:
			string_recved = socket.recv()
						
			
			key = "key_seq_"+str(key_index_seq)
			key_index_seq = key_index_seq +1 
			## To store data 'seq_2' with a key 'key_ran' in reddis DB
			redis_db.set(key, string_recved) 
			
			

	except KeyboardInterrupt:
		print("stopped")

	sys.exit(1)

def thread_ran_seq_6():
	global kill, redis_db, key_index_seq##, flag_request
	

	context = zmq.Context()
	socket = context.socket(zmq.SUB)

	socket.connect("ipc:///tmp/socket_logging_seq_6")
	topicfilter = ""

	socket.setsockopt_string(zmq.SUBSCRIBE, topicfilter)
	key_index = 0

	try:
		while not kill:
			string_recved = socket.recv()
			
			key = "key_seq_"+str(key_index_seq)
			key_index_seq = key_index_seq +1 
			## To store data 'seq_2' with a key 'key_ran' in reddis DB
			redis_db.set(key, string_recved) 
			
			

	except KeyboardInterrupt:
		print("stopped")

	sys.exit(1)



def thread_ric_seq():
	global kill, redis_db, key_index_seq ##, flag_request
	

	context = zmq.Context()
	socket = context.socket(zmq.SUB)

	socket.connect("ipc:///tmp/socket_logging_seq_ric")
	topicfilter = ""

	socket.setsockopt_string(zmq.SUBSCRIBE, topicfilter)
	key_index = 0

	try:
		while not kill:
						
			string_recved = socket.recv()
						
			key = "key_seq_"+str(key_index_seq)
			key_index_seq = key_index_seq +1 
			## To store data 'seq_2' with a key 'key_ran' in reddis DB
			redis_db.set(key, string_recved) 
			
			

	except KeyboardInterrupt:
		print("stopped")

	sys.exit(1)


def thread_app_seq_1():
	global kill, redis_db, key_index_seq ##, flag_request
	

	context = zmq.Context()
	socket = context.socket(zmq.SUB)

	socket.connect("ipc:///tmp/socket_mbuff_1")
	topicfilter = ""

	socket.setsockopt_string(zmq.SUBSCRIBE, topicfilter)
	key_index = 0

	try:
		while not kill:
						
			string_recved = socket.recv()
			string_recved = str(time.time()) + ",\t"+ "8"+ ",\t" + str(string_recved)
						
			key = "key_seq_"+str(key_index_seq)
			key_index_seq = key_index_seq +1 
			## To store data 'seq_2' with a key 'key_ran' in reddis DB
			redis_db.set(key, string_recved) 
			
			

	except KeyboardInterrupt:
		print("stopped")

	sys.exit(1)


def thread_app_seq_2():
	global kill, redis_db, key_index_seq ##, flag_request
	

	context = zmq.Context()
	socket = context.socket(zmq.SUB)

	socket.connect("ipc:///tmp/socket_mbuff_2")
	topicfilter = ""

	socket.setsockopt_string(zmq.SUBSCRIBE, topicfilter)
	key_index = 0

	try:
		while not kill:
						
			string_recved = socket.recv()
			string_recved = str(time.time()) + ",\t"+ "9"+ ",\t" + str(string_recved)
						
			key = "key_seq_"+str(key_index_seq)
			key_index_seq = key_index_seq +1 
			## To store data 'seq_2' with a key 'key_ran' in reddis DB
			redis_db.set(key, string_recved) 
			
			

	except KeyboardInterrupt:
		print("stopped")

	sys.exit(1)


def update(frame):
	global  thrpt, max_y, redis_db
	
	#print(thrpt)
	
	x.append(x[-1] +1)
	y.append(thrpt)
	plt.axis([0,len(x),0,max_y])
	
	algo = redis_db.get('algo')
	#print(algo)
	if (algo == None): 
		algo = "b'Half resource for each UE'"

	plt.title("Scheduler" + str(algo).replace("b'", " : ").replace("'", ""))


	ln.set_data(x,y)
	return ln, 

def main():
	global  kill,  redis_db, key_index_seq, thrpt
	
	
	
	


	key_index_seq = 0 
	print('main')
	
	t_ran_metrics = Thread(target = thread_ran_metrics)
	t_ric_weights = Thread(target = thread_ric_weights)
	
	t_ran_seq = Thread(target = thread_ran_seq)
	t_ran_seq_6 = Thread(target = thread_ran_seq_6)
	t_ric_seq = Thread(target = thread_ric_seq)
	t_app_seq_1 = Thread(target = thread_app_seq_1)
	t_app_seq_2 = Thread(target = thread_app_seq_2)
	
	t_ran_metrics.start()
	t_ric_weights.start()

	t_ran_seq.start()
	t_ran_seq_6.start()
	t_ric_seq.start()
	t_app_seq_1.start()
	t_app_seq_2.start()
	
	


	ani = FuncAnimation(fig, update, interval=1000)

	plt.xlabel("Time [Sec]")
	plt.ylabel("Throughput [Mbps]")

	plt.tight_layout()
	plt.grid()
	plt.show()

	
if __name__=='__main__':
	
	main()




