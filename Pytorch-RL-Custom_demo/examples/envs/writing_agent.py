import zmq
import time 
import sys
from threading import Thread

## before you import redis you have to install redis on your system by pip install redis
import redis

kill = False

## To connect to a redis server
redis_db = redis.StrictRedis(host = 'localhost', port=6379, decode_responses = False, db=0)

is_end_ran = False
key_index_ran = 0

f_ran = open("log_ran.txt","w")

while(not is_end_ran):
	key_ran = "key_ran_metrics_"+str(key_index_ran)
	data_bytes = redis_db.get(key_ran)

	if data_bytes is None:
		print("Number of data from RAN", key_index_ran)
		break

	else: 
		data_str = str(data_bytes).replace(" ",",").replace("\\t","").replace("b\"","").replace("b'","").replace("\\n'","").replace("\\x00'","").replace(",\\\"","").replace("\\\"","").replace("\\","")
		f_ran.write(data_str+"\n")
		key_index_ran = key_index_ran + 1


f_ric = open("log_ric.txt","w")
is_end_ric = False
key_index_ric = 0

while(not is_end_ric):
	key_ric = "key_ric_weights_"+str(key_index_ric)
	data_bytes = redis_db.get(key_ric)

	if data_bytes is None:
		print("Number of data from RIC ", key_index_ric)
		break

	else: 
		data_str = str(data_bytes).replace(" ",",").replace("\\t","").replace("b\"","").replace("b'","").replace("\\n'","").replace(",'\"","")
		f_ric.write(data_str+"\n")
		key_index_ric = key_index_ric + 1



f_seq = open("log_seq.txt","w")
is_end_seq = False
key_index_seq = 0

while(not is_end_seq):
	key_seq = "key_seq_"+str(key_index_seq)
	data_bytes = redis_db.get(key_seq)

	if data_bytes is None:
		print("Number of data for seq ", key_index_seq)
		break

	else: 
		data_str = str(data_bytes).replace("\\t","").replace("b'","").replace("\\n'","").replace("\\x00'","").replace("b\"","").replace("'\"","")
		f_seq.write(data_str+"\n")
		key_index_seq = key_index_seq + 1



f_seq = open("log_dt_rl.txt","w")
is_end_seq = False
key_index_seq = 0

while(not is_end_seq):
	key_seq = "key_dt_"+str(key_index_seq)
	data_bytes = redis_db.get(key_seq)

	if data_bytes is None:
		print("Number of data for rl dt ", key_index_seq)
		break

	else: 
		data_str = str(data_bytes).replace("b'","").replace("\'", "")
		f_seq.write(data_str+"\n")
		key_index_seq = key_index_seq + 1