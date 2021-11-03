from time import sleep
import sys, os

this_dir = os.path.dirname(__file__)
sys.path.append(
    os.path.join(this_dir, 'src'))
sys.path.append(
    os.path.join(this_dir, '..', '..', 'config'))

import cyberswitch_open_command_close as occ
import pb2b_config as cg

sys.path.append(cg.slowdaq_folder)

from slowdaq.pb2 import Publisher

pub = Publisher('Cyberswitch',cg.slowdaq_ip,cg.slowdaq_port)
 
while True:    
    try:
        status = occ.open_command_close('status')
    except BlockingIOError:
        print('Busy port! Trying again...')
        sleep(2)
    
    else:
        if status == True:
            continue
        elif len(status) == 5:
            pub.serve()
            data = pub.pack({'Port 1 status: ':status[0],
                             'Port 2 status: ':status[1],
                             'Port 3 status: ':status[2],
                             'Port 4 status: ':status[3],
                             'Port 5 Status: ':status[4]})
            pub.queue(data)
            print('Sending data...')
            sleep(10)  
        else:
            print('Bad output, trying again...')
            sleep(2)

