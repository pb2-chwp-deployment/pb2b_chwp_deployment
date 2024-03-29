# Slowdaq publisher for the MUX UPS

# Imports
import os, sys
import sys
import time

this_dir = os.path.dirname(__file__)
sys.path.append(
    os.path.join(this_dir, '..', 'config'))
sys.path.append(
    os.path.join(this_dir, 'src'))

import pb2b_config as cg
import mux_ups_controller

# Import Slowdaq
sys.path.append(cg.slowdaq_folder)
from slowdaq.pb2 import Publisher

# Instantiates publisher instance for the ups
pub = Publisher('mux_ups_info', cg.slowdaq_ip, cg.slowdaq_port)
ups = mux_ups_controller.UPS(cg.mux_ups_ip)

index = 0

while True:
    try:
        ups.connect()
        ups.update()
        ups.disconnect()
    except BlockingIOError:
        print('Busy port! Trying again...')
        time.sleep(2)
    else:
        pub.serve()
        data = pub.pack({'output_info': ups.output_info, 'input_info': ups.input_info,
                         'battery_percent': ups.battery_percent, 'battery_temp': ups.battery_temperature,
                         'battery_life': ups.battery_life, 'time': time.time(), 'index': index})
        print('Sending data')
        pub.queue(data)
        index += 1
        time.sleep(10)

