#!/usr/bin/python3
import os, sys, fcntl
import pickle as pkl
from time import sleep

this_dir = os.path.dirname(__file__)
sys.path.append(this_dir)
sys.path.append(
    os.path.join(this_dir, '..', 'config'))
sys.path.append(
    os.path.join(this_dir, '..', 'APC_UPC', 'src'))

import chwp_control as cc
import pb2b_config as cg
import log_control as lg
import ups_controller as uc

class SHUTDOWN:
    def __init__(self, ups_ip, status_pkl):
        self.ups = uc.UPS(ups_ip)
        self.status_pkl = status_pkl
        self._log = lg.Logging()

        try:
            self._load_status()
        except:
            self._log.out('Warning: Status file does not exist, creating new file')
            self.status = {'stopping': True, 'off': True}
            self._set_status()

    def __exit__(self):
        self.status = {'stopping': True, 'off': True}
        self._set_status()

    def monitor(self):
        self.status = {'stopping': False, 'off': False}
        while not self.status['stopping']:
            self.ups.connect()
            self.ups.update()
            self.ups.disconnect()

            if float(self.ups.battery_percent) > 50:
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
                    sleep(1500)
                
                self._log.out('CHWP_Emergency_Shutdown: Waiting 30sec for CHWP to completely stop')
                sleep(30)
                self.cc.cold_grip()
                self._log.out('CHWP_Emergency_Shutdown: Shutdown complete')
        
        self.status = {'stopping': True, 'off': True}
        self._set_status()

    def _load_status(self):
        with open(os.path.join(this_dir, self.status_pkl), 'rb') as status_file:
            self.status = pkl.load(status_file)
        return True

    def _set_status(self):
        with open(os.path.join(this_dir, self.status_pkl), 'wb') as status_file:
            pkl.dump(self.status, status_file)
        return True

chwp_shutdown = SHUTDOWN(cg.ups_ip, cg.status_file)
chwp_shutdown.monitor()
