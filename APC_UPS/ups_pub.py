i# Slowdaq publisher for the MUX UPS

# Imports
import os, sys
from time import sleep

this_dir = os.path.dirname(__file__)
sys.path.append(
    os.path.join(this_dir, '..', 'config'))
sys.path.append(
    os.path.join(this_dir, 'src'))

import pb2b_config as cg
import ups_controller

# Change this to the directory which holds slowdaq
sys.path.append(cg.slowdaq_folder)
from slowdaq.pb2 import Publisher

# Instantiates publisher instance for the ups
pub = Publisher('ups_info', cg.slowdaq_ip, cg.slowdaq_port)
ups = ups_controller.UPS(cg.ups_ip)

while True:
    try:
        ups.connect()
        ups.update()
        ups.disconnect()
    except BlockingIOError:
        print('Busy port! Trying again...')
        sleep(2)
    else:
        pub.serve()
        data = pub.pack({'output_info': ups.output_info, 'input_info': ups.input_info,
                         'battery_percent': ups.battery_percent, 'battery_temp': ups.battery_temperature,
                         'battery_life': ups.battery_life})
        print('Sending data')
        pub.queue(data)
        sleep(10)

