from time import sleep
import sys, os

this_dir = os.path.dirname(__file__)
sys.path.append(
    os.path.join(this_dir, 'src'))
sys.path.append(
    os.path.join(this_dir, '..', '..', 'config'))

import gripper_open_command_close as occ
import pb2b_config as cg

sys.path.append(cg.slowdaq_folder)

from slowdaq.pb2 import Publisher

pub = Publisher('Gripper',cg.slowdaq_ip,cg.slowdaq_port)

while True:
    try:
        status = occ.open_command_close('status')        
    except BlockingIOError:
        print('Busy! Trying again...')
        sleep(2)
    else:
        if type(status) == dict:
            pub.serve()
            data = pub.pack(status)
            pub.queue(data)
            print('Sending data...')
            sleep(10)
        else:
            print('Bad output, trying again...')
            sleep(2)
