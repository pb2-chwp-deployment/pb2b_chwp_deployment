import sys, os
from time import sleep

this_dir = os.path.dirname(__file__)
sys.path.append(this_dir)

import src.pmx_open_command_close as occ

for i in range(30):
	occ.open_command_close('V {}'.format(3.5+i/2.))
	print("Setting Voltage to {} V".format(3.5+i/2.))
	sleep(600)

occ.open_command_close('OFF')
