from time import sleep
import sys, os

this_dir = os.path.dirname(__file__)
sys.path.append(
    os.path.join(this_dir, 'src'))
sys.path.append(
    os.path.join(this_dir, '..', 'config'))

import pmx_open_command_close as occ
import pb2b_config as cg

sys.path.append(cg.slowdaq_folder)

from slowdaq.pb2 import Publisher

pub = Publisher('PMX1',cg.slowdaq_ip,cg.slowdaq_port)

while True:
    try:
        voltage, current = occ.open_command_close('VC?')
        output = occ.open_command_close('O?')[1]
    except BlockingIOError:
        print('Busy port! Trying again...')
        sleep(2)
    else:
        if type(voltage)==float and type(current)==float and type(output)==int:
            pub.serve()
            data = pub.pack({'Measured voltage':voltage,
                             'Measured current':current,
                             'Output status':output})
            print('Sending data')
            pub.queue(data)
            sleep(10)
        else:
            print('Bad outputs! trying again...')
            sleep(2)

