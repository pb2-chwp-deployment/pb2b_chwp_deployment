import sys, os
import time as tm

this_dir = os.path.dirname(__file__)
sys.path.append(
    os.path.join(this_dir, '..', 'config'))
sys.path.append(
    os.path.join(this_dir, 'src'))
sys.path.append(
    os.path.join(this_dir, '..', 'Omega_PID', 'src'))

import pb2b_config as cg
import chwpMonitor as cm
import pid_controller as pc

monitor = cm.CHWPMonitor()
pid = pc.PID(cg.pid_ip, cg.pid_port)

send_sleep = 5
try:
    while True:
        out_dict = {}
        out_dict.update({"FREQ": pid.get_freq()})
        success = monitor.send_data(out_dict)
        tm.sleep(send_sleep)
except KeyboardInterrupt:
    print("Keyboard Interrupt in 'pid_monitor.py'")
finally:
    del monitor
