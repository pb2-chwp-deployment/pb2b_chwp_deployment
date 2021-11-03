import sys, os
import time as tm

this_dir = os.path.dirname(__file__)
sys.path.append(
    os.path.join(this_dir, '..', 'config'))
sys.path.append(
    os.path.join(this_dir, 'src'))
sys.path.append(
    os.path.join(this_dir, '..', 'APC_UPS', 'src'))

import pb2b_config as cg
import chwpMonitor as cm
import ups_controller as uc

monitor = cm.CHWPMonitor()
ups = uc.UPS(cg.ups_ip)

send_sleep = 5
try:
    while True:
        out_dict = {}
        out_dict.update({'output_info': ups.output_info, 'input_info': ups.input_info,
                         'battery_percent': ups.battery_percent, 'battery_temp': ups.battery_temperature,
                         'battery_life': ups.battery_life})
        success = monitor.send_data(out_dict)
        tm.sleep(send_sleep)
    except KeyboardInterrupt:
        print("Keyboard Interrupt in 'ups_monitor.py'")
    finally:
        del monitor
