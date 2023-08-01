import time
import sys
import os

this_dir = os.path.dirname(__file__)
sys.path.append(
    os.path.join(this_dir, '..', 'config'))
sys.path.append(
    os.path.join(this_dir, 'src'))

import pid_controller as pc
import pb2b_config as cg

sys.path.append(cg.slowdaq_folder)

from slowdaq.pb2 import Publisher

pub = Publisher('CHWP_PID', cg.slowdaq_ip, cg.slowdaq_port)
pid = pc.PID(cg.pid_ip, cg.pid_port)

index = 0

while True:
    try:
        hwp_freq = pid.get_freq()
    except BlockingIOError:
        print('Busy port! Trying again...')
        time.sleep(2)
    else:
        if type(hwp_freq) == float or type(hwp_freq) == int:
            pub.serve()
            data = pub.pack({'PID_frequency': hwp_freq, 'time': time.time(), 'index': index})
            print(f'HWP Frequency: {hwp_freq}')
            pub.queue(data)
            index += 1
            time.sleep(10)
        else:
            print('Bad outputs! tyring again...')
            time.sleep(2)

