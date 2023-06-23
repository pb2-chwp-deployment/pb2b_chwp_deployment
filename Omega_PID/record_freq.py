import sys, os
import time as tm
from datetime import datetime

this_dir = os.path.dirname(__file__)
sys.path.append(
	os.path.join(this_dir, 'src'))
sys.path.append(
	os.path.join(this_dir, '..', 'config'))

import pid_controller as pc
import pb2b_config as cg

pid = pc.PID(cg.pid_ip, cg. pid_port)

def timed_read(time, out_file):
	datafile = open(out_file, 'a')
	run_time = 0
	while run_time < time:
		now = datetime.now()
		current_time = now.strftime("%H:%M:%S")
		datafile.write(current_time + ", " + str(pid.get_freq()) + '\n')
		tm.sleep(4)
		print(current_time)
		run_time += 5

timed_read(90*60, '20230129_spindown_no_pid.txt')
