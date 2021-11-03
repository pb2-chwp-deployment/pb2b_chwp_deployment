from time import sleep
import sys, os

this_dir = os.path.dirname(__file__)
sys.path.append(
    os.path.join(this_dir, '..', 'config'))
sys.path.append(
    os.path.join(this_dir, 'src'))

import pid_controller as pc
import pb2b_config as cg

sys.path.append(cg.slowdaq_folder)

from slowdaq.pb2 import Publisher

pub = Publisher('PID_CHWP', cg.slowdaq_ip, cg.slowdaq_port)
pid = pc.PID(cg.pid_ip, cg.pid_port)

while True:
    try:
        hwp_freq = pid.get_freq()
    except BlockingIOError:
        print('Busy port! Trying again...')
        sleep(2)
    else:
        if type(hwp_freq) == float or type(hwp_freq) == int:
            pub.serve()
            data = pub.pack({'PID frequency':hwp_freq})
            print('Sending data')
            pub.queue(data)
            sleep(10)
        else:
            print('Bad outputs! tyring again...')
            sleep(2)

