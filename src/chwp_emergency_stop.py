#!/usr/bin/python3
import os
import sys
import argparse
import fcntl
import pickle as pkl
from time import sleep

this_dir = os.path.dirname(__file__)
sys.path.append(this_dir)
sys.path.append(
    os.path.join(this_dir, '..', 'config'))
sys.path.append(
    os.path.join(this_dir, '..', 'APC_UPS', 'src'))

import chwp_control as cc
import pb2b_config as cg
import log_control as lg
import aux2_ups_controller as uc

class SHUTDOWN:
    def __init__(self, ups_ip, status_pkl):
        self.ups = uc.UPS(ups_ip)
        self.status_pkl = status_pkl
        self._log = lg.Logging()
        self.cc = cc.CHWP_Control()

        try:
            self._load_status()
        except:
            self._log.out('Warning: Status file does not exist, creating new file')
            self.status = {'stopping': True, 'off': True}
            self._set_status()

    def __exit__(self):
        self.status = {'stopping': True, 'off': True}
        self._set_status()

    def monitor(self, verb = False):
        self.status = {'stopping': False, 'off': False}
        self._set_status()
        if verb:
            print()
        while not self.status['stopping']:
            self.ups.update()
            if float(self.ups.batt_capacity) > 80:
                if verb:
                    print(f'Battery capacity: {self.ups.batt_capacity} %                     ', end = '\r')
                sleep(10)
                self._load_status()
            else:
                self._log.out('CHWP_Emergency_Shutdown: UPS Battery below threshold, activating emergency stop')
                self.status['stopping'] = True
                self._set_status()

                if not self.cc.gripper_home():
                    self._log.out('ERROR: Cannot control grippers')
                    self.cc.gripper_reboot()
                    sleep(2)
                    if not self.cc.gripper_home():
                        self._log.out('ERROR: Still cannot control grippers')

                if not self.cc.rotation_stop():
                    self.cc.rotation_off()
                    sleep(1500)
                
                self._log.out('CHWP_Emergency_Shutdown: Waiting 90sec for CHWP to completely stop')
                sleep(90)
                self.cc.cold_grip()
                self.cc.rotation_bias()
                self._log.out('CHWP_Emergency_Shutdown: Shutdown complete')
       
        self.status = {'stopping': True, 'off': True}
        self._set_status()
        print()
        self._log.out('CHWP_Emergency_Shutdown: Monitor Stopped')
        return True

    def _load_status(self):
        with open(os.path.join(this_dir, self.status_pkl), 'rb') as status_file:
            self.status = pkl.load(status_file)
        return True

    def _set_status(self):
        with open(os.path.join(this_dir, self.status_pkl), 'wb') as status_file:
            pkl.dump(self.status, status_file)
        return True

ps = argparse.ArgumentParser(
    description='Emergency stop program for the PB2b CHWP')
ps.add_argument('-v', action = 'store', dest = 'verb', type = int, default = 0)
args = ps.parse_args()

chwp_shutdown = SHUTDOWN(cg.aux2_ups_ip, cg.aux2_status_file)
if len(sys.argv) > 1:
    chwp_shutdown.monitor(verb = args.verb)
else:
    chwp_shutdown.monitor()
