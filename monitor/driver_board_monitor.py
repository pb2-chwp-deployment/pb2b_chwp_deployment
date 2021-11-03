import sys as sy
import time as tm
import os

this_dir = os.path.dirname(__file__)
sy.path.append(os.path.join(this_dir, '..', "config"))
import pb2b_config as cg  # noqa: E402
sy.path.append(os.path.join(this_dir, "src"))
import chwpMonitor as cm  # noqa: E402
sy.path.append(os.path.join(this_dir, '..', "PMX", "src"))
import pmx as px  # noqa: E402


# Establish socket connection to remote slowDAQ publisher
monitor = cm.CHWPMonitor()

# Connect to the driver board PMX power supplies
if cg.use_tcp:
    pmx_arr = [px.PMX(tcp_ip=ip, tcp_port=port)
               for ip, port in zip(cg.kbias_ips, cg.kbias_ports)]
else:
    pmx_arr = [px.PMX(rtu_port=port) for port in cg.rtu_ports]

# Query the gripper status periodically and
# send the data over the socket connection
send_sleep = 100  # sec
try:
    while True:
        # Collect monitoring information
        out_dict = {}
        # Power status
        out_dict.update(
            {("PWR%02d" % (i)): ("%d" % (int(pmx.check_output())))
             for i, pmx in enumerate(pmx_arr)})
        # Output voltage
        out_dict.update(
            {("VOL%02d" % (i)): ("%.05f" % (float(pmx.check_voltage())))
             for i, pmx in enumerate(pmx_arr)})
        # Output current
        out_dict.update(
            {("CUR%02d" % (i)): ("%.05f" % (float(pmx.check_current())))
             for i, pmx in enumerate(pmx_arr)})

        # Send the data
        success = monitor.send_data(out_dict)
        tm.sleep(send_sleep)
except KeyboardInterrupt:
    print("Keyboard Interrupt in 'driver_board_monitor.py'")
finally:
    del monitor
