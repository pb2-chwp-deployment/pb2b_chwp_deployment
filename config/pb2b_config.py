# config file for the PB2b CHWP

#Experiment
exp = 'PB2'

#Dummy variables to prevent errors
rtu_port = 1000
rtu_ports = [1000,1000]
use_tcp = True

#beaglebone black
bb1_username = 'polarbear'
bb1_ip = '192.168.2.55'
bb1_pass = 'pb4000#$'

bb2_username = 'polarbear'
bb2_ip = '192.168.2.56'
bb2_pass = 'pb4000#$'

#cyberswitch
cyberswitch_tcp_ip = '192.168.2.52'
cyberswitch_tcp_port = 4001

#kikusui bias power supply
kbias_ips = ['192.168.2.53', '192.168.2.53']
kbias_ports = [4001, 4002]

#kikusui drive power supply
kdrive_ip = '192.168.2.53'
kdrive_port = 4003

#grippers
gripper_ip = '192.168.2.52'
gripper_port = 4002

#pid controller
pid_ip = '192.168.2.58'
pid_port = '2000'

pid_tune_p = 0.2
pid_tune_i = 63
pid_tune_d = 0

pid_stop_p = 0.2
pid_stop_i = 0
pid_stop_d = 0

#slowdaq
slowdaq_folder = '/home/polarbear/slowdaq_pb2b'
slowdaq_ip = '192.168.2.102'
slowdaq_port = 3141
slowdaq_conn_attempts = 5

#ups
mux_ups_ip = '192.168.2.60'
mux_status_file = 'mux_status.pkl'
aux2_ups_ip = '192.168.2.59'
aux2_status_file = 'aux2_status.pkl'
