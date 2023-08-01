# Slowdaq publisher for the AUX2 UPS

# Imports
import os
import sys
import time

this_dir = os.path.dirname(__file__)
sys.path.append(
	os.path.join(this_dir, '..', 'config'))
sys.path.append(
	os.path.join(this_dir, 'src'))

import pb2b_config as cg
import aux2_ups_controller

# Import Slowdaq
sys.path.append(cg.slowdaq_folder)
from slowdaq.pb2 import Publisher

# Instantiates publisher instance for the ups
pub = Publisher('PB2B_AUX2_UPS', cg.slowdaq_ip, cg.slowdaq_port)
ups = aux2_ups_controller.UPS(cg.aux2_ups_ip)

index = 0

while True:
    try:
        ups.update()
    except:
        print('Connection Error! Trying again...')
        time.sleep(2)
    else:
        pub.serve()
        data_dict = {'input_voltage': ups.input_voltage,
                     'input_freq': ups.input_freq,
                     'batt_capacity': ups.batt_capacity,
                     'output_status': ups.output_status,
                     'output_voltage': ups.output_voltage,
                     'output_freq': ups.output_freq,
                     'output_load': ups.output_load}
        data_dict['time'] = time.time()
        data_dict['index'] = index

        print('PB2b AUX2 UPS: Status')
        for key in data_dict.keys():
            print(f'{key}: {data_dict[key]}')
        print('')

        data = pub.pack(data_dict)
        pub.queue(data)
        index += 1
        time.sleep(10)
