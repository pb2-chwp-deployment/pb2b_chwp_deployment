# Built-in python modules
import datetime as dt
import time as tm
import numpy as np
import sys as sy
import pickle as pkl
import os
import readline
import subprocess

# CHWP control modules
this_dir = os.path.dirname(__file__)
sy.path.append(
    os.path.join(this_dir, "..", "Gripper", "src"))
sy.path.append(
    os.path.join(this_dir, "..", "Cyberswitch", "src"))
sy.path.append(
    os.path.join(this_dir, "..", "Omega_PID", "src"))
sy.path.append(
    os.path.join(this_dir, "..", "PMX", "src"))
sy.path.append(
    os.path.join(this_dir, "..", "config"))

import gripper as gp  # noqa: E402
import NP_05B as cs  # noqa: E402
import log_control as lg  # noqa: E402
import pid_controller as pc
import pmx_open_command_close as occ
import pb2b_config as cg

class CHWP_Control:
    def __init__(self):
        # Connect to the gripper using default settings
        self.GPR = gp.Gripper()
        self.CS = cs.NP_05B()
        self._pos_file = os.path.join(
            this_dir, '..', "POS", "chwp_control_positions.txt")
        self._read_pos()
        self._log = lg.Logging()
        self.pid = pc.PID()
        self._pid_direction = True
        return

    def __del__(self):
        self._write_pos()
        return

    # ***** Public Methods *****
    def warm_grip(self):
        """ Squeeze the rotor assuming it is supported """
        self._squeeze(0.1)
        self._pos_from_user(mode="Warm_Centered")
        return self.GPR.OFF()

    def cooldown_grip(self, time_incr=3600.):
        """ Squeeze the rotor little by little every hour """
        while True:  # User must exit this program
            try:
                # Move each gripper backwards first
                #for i in range(1, 4):
                #    self.GPR.MOVE('POS', -0.1, i)
                # Then, re-squeeze the rotor
                result = self._squeeze(0.1)

                if result:
                    self._log.out(
                        "CHWP_Control.cooldown_grip(): Rotor regripped")
                    self.GPR.OFF()
                    self._sleep(time_incr)
                    continue
                else:
                    self._log.out(
                        "ERROR: failed to regrip the rotor")
                    return False
            except KeyboardInterrupt:
                self._pos_from_user(mode="Cooldown_Finish")
                break
        return self.GPR.OFF()

    def cold_grip(self):
        """ Grip the CHWP while cold, assuming it will warm up """
        # First squeeze the rotor
        self._squeeze(1.0)
        # Then backup by 1 mm to allow some compliance
        # for rotor expansion during warmup
        for i in range(1, 4):
            self.GPR.MOVE('POS', -1.0, i)
        # Turn off the motors
        return self.GPR.OFF()

    def cold_ungrip(self):
        """ Ungrip the CHWP after cooling is finished """
        self._pos_from_user(mode="Cold_Ungrip")
        self._release()
        self._log.out("CHWP_Control.cold_ungrip(): Rotor ungripped")
        return self.GPR.OFF()

    def gripper_home(self):
        """ Home the grippers """
        self.GPR.HOME()
        self._log.out("CHWP_Control.griper_home(): Gripper homed")
        return self.GPR.OFF()

    def gripper_reboot(self):
        """ Reboot the CHWP electronics """
        self.CS.OFF(1)
        self.CS.OFF(2)
        self.CS.OFF(3)
        self.CS.ON(1)
        self.CS.ON(2)
        self.CS.ON(3)
        self._log.out("CHWP_Control.gripper_reboot(): Gripper control rebooted")
        return

    def rotation_direction(self, direction = True):
        if direction:
            self.pid.set_direction('0')
            self._pid_direction = True
            self._log.out("CHWP_Control.rotation_direction(): CHWP direction set to forward")
            return True
        elif not direction:
            self.pid.set_direction('1')
            self._pid_direction = False
            self._log.out("CHWP_Control.rotation_direction(): CHWP direction set to reverse")
            return True
        else:
            self._log.out("ERROR: Invalid direction entered")
            return False

    def rotation_stop(self):
        try:
            self._rotation_mode('PID')
            self.rotation_direction(not self._pid_direction)
            self.pid.tune_stop()
            occ.open_command_close('ON')
            tm.sleep(1)
            cur_freq = self.pid.get_freq()
            start_time = tm.perf_counter()
            while cur_freq > 0.15:
                cur_freq = self.pid.get_freq()
                print('Current Frequency =', cur_freq, 'Hz    ', end = '\r')
                if abs(start_time - tm.perf_counter()) > 100:
                    occ.open_command_close('OFF')
                    self._log.err("CHWP_Control.rotation_stop(): Stop took too long")
                    return False
            occ.open_command_close('OFF')
            self.rotation_direction(self._pid_direction)
            print(' '*30 end = '\r')
            print('CHWP stopped')
            self._log.out("CHWP_Control.rotation_stop(): CHWP stopped")
            return True
        except KeyboardInterrupt:
            occ.open_command_close('OFF')
            self._log.err("CHWP_Control.rotation_stop(): User interrupt")
            return False

    def rotation_spin(self, frequency = 0.0):
        if float(frequency) <= 3.5:
            try:
                print('Starting time is {}'.format(tm.time()))
                self._rotation_mode('PID')
                self.rotation_direction(self._pid_direction)
                self.pid.declare_freq(float(frequency))
                self.pid.tune_freq()
                occ.open_command_close('ON')
                tm.sleep(1)
                cur_freq = self.pid.get_freq()
                while abs(cur_freq - frequency) > 0.005:
                    cur_freq = self.pid.get_freq()
                    print('Current Frequency =', cur_freq, 'Hz    ', end = '\r')
                print(' '*30, end = '\r')
                print('Tuning finished')
                self._log.out("CHWP_Control.rotation_spin(): Tuning finished")
                return True
            except KeyboardInterrupt:
                self._log.err("CHWP_Control.rotation_spin(): User interrupt")
                return False
        else:
            pass

    def rotation_voltage(self, voltage = 0.0):
        if float(voltage) <= 32.0:
            self._rotation_mode('VOLT')
            self.rotation_direction(self._pid_direction)
            occ.open_command_close('V {}'.format(voltage))
            occ.open_command_close('ON')
            self._log.out("CHWP_Control.rotation_voltage(): CHWP drive voltage set to {} volts".format(voltage))
            self._log.out()
            return True
        else:
            self._log.out("ERROR: Invalid voltage entered")
            return False

    def rotation_off(self):
        occ.open_command_close('OFF')
        self._log.out("CHWP_Control.rotation_off(): Drive power turned off")
        return True

    def bb_packet_collect(self):
        subprocess.call([os.path.join(this_dir, 'bb_packet_collect'), cg.bb1_username, cg.bb1_ip, cg.bb1_pass],
                         stderr = subprocess.DEVNULL)
        subprocess.call([os.path.join(this_dir, 'bb_packet_collect'), cg.bb2_username, cg.bb2_ip, cg.bb2_pass],
                         stderr = subprocess.DEVNULL)
        self._log.out("CHWP_Control.bb_packet_collect(): Beaglebone PRUs Enabled")
        return True

    def start_emergency_monitor(self):
        with open(os.path.join(this_dir, cg.status_file), 'rb') as status_file:
            status = pkl.load(status_file)
            if status['off'] == False:
                self._log.out('CHWP_Control.start_emergency_monitor(): Monitor already running')
                return False
        subprocess.call(['nohup', os.path.join(this_dir, 'chwp_emergency_stop.py'), '&'])
        self._log.out('CHWP_Control.start_emergency_monitor(): Monitor started')
        return True

    def stop_emergency_monitor(self):
        with open(os.path.join(this_dir, cg.status_file), 'wb') as status_file:
            status = pkl.load(status_file)
            if status['off'] == True:
                self._log.out('CHWP_Control.stop_emergency_monitor(): Monitor already stopped')
                return False
            elif status['off'] == False and status['stopping'] = True:
                self._log.out('CHWP_Control.stop_emergency_monitor(): Emergency shutdown in progress')
                return False
            else:
                status['stopping'] = True
                pkl.dump(status, status_file)
                self._log.out('CHWP_Control.stop_emergency_monitor(): Stopping monitor')
                return True

    # ***** Private Methods *****
    def _rotation_mode(self, mode = 'PID'):
        if mode == 'PID':
            occ.open_command_close('U')
            self._log.out("CHWP_Control.rotation_mode(): CHWP set to PID control")
            return True
        elif mode == 'VOLT':
            occ.open_command_close('I')
            self._log.out("CHWP_Control.rotation_mode(): CHWP set to direct voltage control")
            return True
        else:
            self._log.out("ERROR: Invalid mode entered")
            return False

    def _sleep(self, duration=3600.):
        """ Sleep in specified increments """
        granular_time = 60.
        for i in range(int(duration / granular_time) + 1):
            tm.sleep(granular_time)
        return

    def _squeeze(self, incr=0.1):
        """ Squeeze the rotor by pushing little by little (incr) """
        in_position = [False for i in range(3)]
        finished = [False for i in range(3)]
        # Iterate through all motors at least once
        first_pass = True
        while not all(finished):
            for i in range(3):
                try:
                    if not finished[i] or first_pass:
                        in_position = self._push(incr, i + 1)
                        if in_position[i]:
                            continue
                        elif not in_position[i]:
                            self.GPR.RESET()
                            finished[i] = True
                    else:
                        continue
                except KeyboardInterrupt:
                    self._log.err(
                        "CHWP_Control._squeeze(): User interrupt")
                    return True
            first_pass = False
        self._log.out(
            "CHWP_Control._squeeze(): Finished squeezing")
        return True

    def _push(self, incr, axis):
        """ Push a given axis forward a given amount """
        self.GPR.MOVE('PUSH', incr, axis)
        inps = self.GPR.INP()
        return inps

    def _release(self, incr=0.1):
        """ Home the motors """
        return self.GPR.HOME()

    def _pos_from_user(self, mode=None):
        """ Obtain manually-inputted motor positions """
        if mode is None:
            self._log.err(
                "CHWP_Control._pos_from_user(): No moving mode passed")
            return False
        pos_arr = []
        for i in range(1, 4):
            pos_inp = input("Position of Axis %d: " % (i))
            try:
                pos_arr.append(float(pos_inp))
            except:
                self._log.err(
                    "Passed position %s is not a float" % (pos_inp))
                return False
        self.pos[mode] = pos_arr
        return True

    def _write_pos(self):
        """ Write positions to file """
        for k in self.pos.keys():
            self._posf.write(
                "%-20s%-10.1f%-10.1f%-10.1f\n"
                % (k, self.pos[k][0], self.pos[k][1],
                   self.pos[k][2]))
        return

    def _read_pos(self):
        """ Read motor positions """
        if (not os.path.exists(self._pos_file) or
           not os.path.getsize(self._pos_file)):
            self.pos = {}
        else:
            pos_data = np.loadtxt(self._pos_file, unpack=True, dtype=np.str)
            self.pos = {
                pos_data[0][i]: [
                    float(pos_data[1][i]),
                    float(pos_data[2][i]),
                    float(pos_data[3][i])]
                for i in range(len(pos_data[0]))}
        self._posf = open(self._pos_file, 'a')
        return
