# config file for the PB2b CHWP

#Experiment
exp = 'PB2'

#Dummy variables to prevent errors
rtu_port = 1000
rtu_ports = [1000,1000]
use_tcp = True

#beaglebone black
bb1_username = 'polarbear'
bb1_ip = '192.168.2.56'
bb1_pass = 'pb4000#$'

bb2_username = 'polarbear'
bb2_ip = '192.168.2.57'
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
slowdaq_folder = '/home/polarbear/slowdaq'
slowdaq_ip = '192.168.2.109'
slowdaq_port = 8000
slowdaq_conn_attempts = 5

#ups
ups_ip = '192.168.2.60'
status_file = 'status.pkl'
