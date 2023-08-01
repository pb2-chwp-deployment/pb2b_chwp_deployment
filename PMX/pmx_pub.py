import time
import sys
import os

this_dir = os.path.dirname(__file__)
sys.path.append(
    os.path.join(this_dir, 'src'))
sys.path.append(
    os.path.join(this_dir, '..', 'config'))

import pmx_open_command_close as occ
import pb2b_config as cg

sys.path.append(cg.slowdaq_folder)

from slowdaq.pb2 import Publisher

pub = Publisher('CHWP_PMX',cg.slowdaq_ip,cg.slowdaq_port)

index = 0

while True:
    try:
        d_voltage, d_current = occ.open_command_close('VC?')
        d_output = occ.open_command_close('O?')[1]
        b1_voltage, b1_current = occ.open_command_close('VC?',ip=cg.kbias_ips[0],
							port=cg.kbias_ports[0],
							lock='.bias1_port_busy')
        b1_output = occ.open_command_close('O?',ip=cg.kbias_ips[0],
					   port=cg.kbias_ports[0],
					   lock='.bias1_port_busy')[1]
        b2_voltage, b2_current = occ.open_command_close('VC?',ip=cg.kbias_ips[1],
							port=cg.kbias_ports[1],
							lock='.bias2_port_busy')
        b2_output = occ.open_command_close('O?',ip=cg.kbias_ips[1],
					   port=cg.kbias_ports[1],
					   lock='.bias2_port_busy')[1]
    except BlockingIOError:
        print('Busy port! Trying again...')
        time.sleep(2)
    else:
        if type(d_voltage)==float and type(d_current)==float and type(d_output)==int:
            pub.serve()
            data = pub.pack({'Drive Kikusui': {'Measured voltage':d_voltage,
                             		       'Measured current':d_current,
                             		       'Output status':d_output},
			     'Bias1 Kikusui': {'Measured voltage': b1_voltage,
                             		       'Measured current':b1_current,
                             		       'Output status':b1_output},
			     'Bias2 Kikusui': {'Measured voltage': b2_voltage,
                             		       'Measured current':b2_current,
                             		       'Output status':b2_output},
                             'time': time.time(), 'index': index})
            pub.queue(data)
            index += 1
            time.sleep(10)
        else:
            print('Bad outputs! trying again...')
            time.sleep(2)

