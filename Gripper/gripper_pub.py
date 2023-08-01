import time 
import sys
import  os

this_dir = os.path.dirname(__file__)
sys.path.append(
    os.path.join(this_dir, 'src'))
sys.path.append(
    os.path.join(this_dir, '..', '..', 'config'))

import gripper_open_command_close as occ
import pb2b_config as cg

sys.path.append(cg.slowdaq_folder)

from slowdaq.pb2 import Publisher

pub = Publisher('CHWP_Gripper',cg.slowdaq_ip,cg.slowdaq_port)

while True:
    try:
        status = occ.open_command_close('status')        
    except BlockingIOError:
        print('Busy! Trying again...')
        time.sleep(2)
    else:
        if type(status) == dict:
            pub.serve()
            status['time'] - time.time()
            data = pub.pack(status)
            pub.queue(data)
            print('Sending data...')
            time.sleep(10)
        else:
            print('Bad output, trying again...')
            time.sleep(2)
