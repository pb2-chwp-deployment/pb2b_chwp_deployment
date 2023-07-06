# Built-in python modules
import datetime as dt
import numpy as np
import pickle as pkl
import sys
import time
import os
import readline
import subprocess

# CHWP control modules
this_dir = os.path.dirname(__file__)
sys.path.append(
    os.path.join(this_dir, "..", "Gripper", "src"))
sys.path.append(
    os.path.join(this_dir, "..", "Cyberswitch", "src"))
sys.path.append(
    os.path.join(this_dir, "..", "Omega_PID", "src"))
sys.path.append(
    os.path.join(this_dir, "..", "PMX", "src"))
sys.path.append(
    os.path.join(this_dir, "..", "config"))

import cyberswitch_open_command_close as cocc  # noqa: E402
import log_control as lg  # noqa: E402
import pid_controller as pc
import pmx_open_command_close as pocc
import gripper_open_command_close as gocc
import pb2b_config as cg


class CHWP_Control:
    def __init__(self):
        # Connect to the gripper using default settings
        self._pos_file = os.path.join(
            this_dir, '..', 'Gripper', "POS", "chwp_control_positions.txt")
        self._read_pos()
        self._log = lg.Logging()

        old_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')
        self.pid = pc.PID(cg.pid_ip, cg.pid_port)
        sys.stdout = old_stdout
        self._pid_direction = 'forward'

        self.bbs = {'encoder1': None,
                    'encoder2': None}

        self.monitor = None

        self.pubs = {'aux2_ups': None,
                     'cyberswitch': None,
                     'gripper': None,
                     'pid': None,
                     'pmx': None}
        return

    def __exit__(self):
        self._write_pos()
        self.slowdaq_publishers_stop()
        self.bb_packet_collect_stop()
        return

    # ***** Public Methods *****
    def warm_grip(self):
        """ Squeeze the rotor assuming it is supported """
        self._squeeze(0.1)
        self._pos_from_user(mode="Warm_Centered")
        return gocc.open_command_close('OFF')

    def cooldown_grip(self, time_incr=3600.):
        """ Squeeze the rotor little by little every hour """
        while True:  # User must exit this program
            try:
                result = self._squeeze(0.1)

                if result:
                    self._log.out(
                        "CHWP_Control.cooldown_grip(): Rotor regripped")
                    gocc.open_command_close('OFF')
                    self._sleep(time_incr)
                    continue
                else:
                    self._log.out(
                        "ERROR: failed to regrip the rotor")
                    return False
            except KeyboardInterrupt:
                self._pos_from_user(mode="Cooldown_Finish")
                break
        
        return gocc.open_command_close('OFF')

    def cold_grip(self):
        """ Grip the CHWP while cold, assuming it will warm up """
        # First squeeze the rotor
        self._squeeze(1.0)
        # Then backup by 1 mm to allow some compliance
        # for rotor expansion during warmup
        for i in range(1, 4):
            gocc.open_command_close(f'MOVE POS {i} -1.0')
        # Turn off the motors
        return gocc.open_command_close('OFF')

    def cold_ungrip(self):
        """ Ungrip the CHWP after cooling is finished """
        self._pos_from_user(mode="Cold_Ungrip")
        self._release()
        self._log.out("CHWP_Control.cold_ungrip(): Rotor ungripped")
        return gocc.open_command_close('OFF')

    def gripper_home(self):
        """ Home the grippers """
        gocc.open_command_close('HOME')
        self._log.out("CHWP_Control.griper_home(): Gripper homed")
        return gocc.open_command_close('OFF')

    def gripper_alarm(self):
        """ Query the alarm state """
        cur_alarm = gocc.open_command_close('ALARM')
        self._log.out(f'Total alarm state: {cur_alarm}')
        self._log.out("CHWP_Control.gripper_alarm(): Gripper alarm queried")
        return True

    def gripper_reset(self):
        """ Reset the gripper alarm """
        gocc.open_command_close('RESET')
        self._log.out("CHWP_Control.gripper_reset(): Gripper controller reset")
        return True

    def gripper_reboot(self):
        """ Reboot the CHWP electronics """
        cocc.open_command_close('ALL OFF')
        cocc.open_command_close('ALL ON')
        self._log.out("CHWP_Control.gripper_reboot(): Gripper control rebooted")
        return True

    def rotation_bias(self, power = 'off'):
        if type(power) is not str:
            self._log.out('Invalid argument type')
            return False

        if power.lower() not in ['on', 'off']:
            self._log.out('Invalid argument value')
            return False

        try:
            pocc.open_command_close(power,ip=cg.kbias_ips[0],
                                   port=cg.kbias_ports[0],
                                   lock='.bias1_port_busy')
            pocc.open_command_close(power,ip=cg.kbias_ips[1],
                                   port=cg.kbias_ports[1],
                                   lock='.bias2_port_busy')
            self._log.out(f"CHWP_Control.rotation_bias(): Bias power supply status changed to: {power}")
            return True
        except BlockingIOError:
            self._log.out('Blocking Error, trying again')
            time.sleep(0.5)
            self.rotation_bias(power = power)
        
        return False

    def rotation_direction(self, direction = 'forward'):
        if type(direction) is not str:
            self._log.out('Invalid argument type')
            return False

        if direction.lower() not in ['forward','reverse']:
            self._log.out('Invalid argument value')
            return False
        
        if direction == 'forward':
            self.pid.set_direction('0')
            self._pid_direction = 'forward'
            self._log.out("CHWP_Control.rotation_direction(): CHWP direction set to forward")
            return True
        elif direction == 'reverse':
            self.pid.set_direction('1')
            self._pid_direction = 'reverse'
            self._log.out("CHWP_Control.rotation_direction(): CHWP direction set to reverse")
            return True

    def rotation_status(self):
        cur_vc = pocc.open_command_close('VC?')
        cur_out = pocc.open_command_close('O?')
        cur_freq = self.pid.get_freq()
        cur_out_bias1 = pocc.open_command_close('O?',ip=cg.kbias_ips[0],
                                                port=cg.kbias_ports[0],
                                                lock='.bias1_port_busy')
        cur_out_bias2 = pocc.open_command_close('O?',ip=cg.kbias_ips[1],
                                                port=cg.kbias_ports[1],
                                                lock='.bias2_port_busy')
        self._log.out(f'PMX Voltage: {cur_vc[0]} V')
        self._log.out(f'PMX Current: {cur_vc[1]} A')
        self._log.out(f'PMX Drive Output: {cur_out[0]}')
        self._log.out(f'PMX Bias1 Output: {cur_out_bias1[0]}')
        self._log.out(f'PMX Bias2 Output: {cur_out_bias2[0]}')
        self._log.out(f'Rotation Frequency: {cur_freq} Hz')
        self._log.out(f'Rotation Direction: {self._pid_direction}')
        return True

    def rotation_stop(self):
        try:
            self._rotation_mode('PID')
            
            if self._pid_direction == 'forward':
                self.rotation_direction(direction = 'reverse')
            else:
                self.rotation_direction(direction = 'forward')
            
            self.pid.tune_stop()
            pocc.open_command_close('ON')
            time.sleep(1)
            cur_freq = self.pid.get_freq()
            self._log.out(f'Starting Frequency: {cur_freq} Hz')
            start_time = time.perf_counter()
            
            while cur_freq > 0.15:
                cur_freq = self.pid.get_freq()
                print('Current Frequency =', cur_freq, 'Hz    ', end = '\r')
            
                if abs(start_time - time.perf_counter()) > 100:
                    pocc.open_command_close('OFF')
                    self._log.err("CHWP_Control.rotation_stop(): Stop took too long")
                    return False
            
            pocc.open_command_close('OFF')
            
            if self._pid_direction == 'forward':
                self.rotation_direction(direction = 'reverse')
            else:
                self.rotation_direction(direction = 'forward')
            
            print(' '*30, end = '\r')
            self._log.out("CHWP_Control.rotation_stop(): CHWP stopped")
            return True
        except KeyboardInterrupt:
            pocc.open_command_close('OFF')
            self._log.err("CHWP_Control.rotation_stop(): User interrupt")
            return False

    def rotation_spin(self, frequency = 0.0):
        if type(frequency) not in [int, float]:
            self_log.out('Invalid argument type')
            return False
        
        if float(frequency) <= 3.5:
            try:
                self._log.out('Starting time is {}'.format(time.time()))
                self._rotation_mode('PID')
                self.rotation_direction(self._pid_direction)
                self.pid.declare_freq(float(frequency))
                self.pid.tune_freq()
                pocc.open_command_close('ON')
                time.sleep(1)
                cur_freq = self.pid.get_freq()
                
                while abs(cur_freq - frequency) > 0.005:
                    cur_freq = self.pid.get_freq()
                    print('Current Frequency =', cur_freq, 'Hz    ', end = '\r')
                
                print(' '*30, end = '\r')
                self._log.out("CHWP_Control.rotation_spin(): Tuning finished")
                return True
            except KeyboardInterrupt:
                pocc.open_command_close('OFF')
                self._log.err("CHWP_Control.rotation_spin(): User interrupt")
                return False
        else:
            self._log.out('Invalid argument value')
            return False

    def rotation_voltage(self, voltage = 0.0):
        if type(voltage) not in [float, int]:
            self._log.out('Invalid argument type')
            return False
        
        if float(voltage) <= 32.0 and float(voltage) >= 0.0:
            self._rotation_mode('VOLT')
            self.rotation_direction(self._pid_direction)
            pocc.open_command_close('V {}'.format(voltage))
            pocc.open_command_close('ON')
            self._log.out("CHWP_Control.rotation_voltage(): CHWP drive voltage set to {} volts".format(voltage))
            return True
        else:
            self._log.out("Invalid argument value")
            return False

    def rotation_off(self):
        pocc.open_command_close('OFF')
        self._log.out("CHWP_Control.rotation_off(): Drive power turned off")
        return True

    def bb_reboot(self, index = 0):
        if type(index) is not int:
            self._log.out('Invalid argument type')
            return False

        if index not in [0, 1, 2]:
            self._log.out('Invalid argument value')
            return False
        
        if index in [0, 1]:
            subprocess.call([os.path.join(this_dir, 'bb_reboot'),
                            cg.bb1_username, cg.bb1_ip, cg.bb1_pass],
                            stderr = subprocess.DEVNULL)
            self._log.out('Beaglebone1 rebooted')

        if index in [0, 2]:
            subprocess.call([os.path.join(this_dir, 'bb_reboot'),
                            cg.bb2_username, cg.bb2_ip, cg.bb2_pass],
                            stderr = subprocess.DEVNULL)
            self._log.out('Beaglebone2 rebooted')

        self._log.out('CHWP_Control.bb_reboot(): Beaglebone reboot')
        return True

    def bb_packet_collect_start(self, index = 0):
        if type(index) is not int:
            self._log.out('Invalid argument type')
            return False

        if index not in [0, 1, 2]:
            self._log.out('Invalid argument value')
            return False

        if index in [0, 1]:
            if self.bbs['encoder1'] is not None:
                self._log.out('Beaglebone1 packet collect already running')
            else:
                self.bbs['encoder1'] = subprocess.Popen([os.path.join(this_dir, 'bb_packet_collect'), 
                                                        cg.bb1_username, cg.bb1_ip, cg.bb1_pass],
                                                        stderr = subprocess.DEVNULL)
                self._log.out('Beaglebone1 packet collect started')
        
        if index in [0, 2]:
            if self.bbs['encoder2'] is not None:
                self._log.out('Beaglebone2 packet collect already running')
            else:
                self.bbs['encoder2'] = subprocess.Popen([os.path.join(this_dir, 'bb_packet_collect'), 
                                                        cg.bb2_username, cg.bb2_ip, cg.bb2_pass],
                                                        stderr = subprocess.DEVNULL)
                self._log.out('Beaglebone2 packet collect started')
        
        self._log.out("CHWP_Control.bb_packet_collect_start(): Beaglebone PRUs Enabled")
        return True

    def bb_packet_collect_stop(self):
        for key in self.bbs.keys():
            if self.bbs[key] is not None:
                self.bbs[key].kill()
                self._log.out(f'{key}: Beaglebone process killed')
        
        self._log.out('CHWP_Control.bb_packet_collect_stop(): Beaglebone processes ended')
        return True

    def emergency_monitor_start(self, verb = '0'):
        if type(verb) not in [int, str]:
            self._log.out('Invalid argument type')
            return False
        
        if str(verb) not in ['0','1']:
            self._log.out('Invalid argument value')
            return False

        with open(os.path.join(this_dir, cg.aux2_status_file), 'rb') as status_file:
            status = pkl.load(status_file)
            if status['stopping'] == False:
                self._log.out('CHWP_Control.emergency_monitor_start(): Monitor already running')
                return False
        
        self.monitor = subprocess.Popen(['python3', os.path.join(this_dir, 'chwp_emergency_stop.py'), '-v', str(verb)])
        self._log.out('CHWP_Control.emergency_monitor_start(): Monitor started')
        return True

    def emergency_monitor_stop(self):
        with open(os.path.join(this_dir, cg.aux2_status_file), 'rb') as status_file:
            status = pkl.load(status_file)
            
            if status['off']:
                self._log.out('CHWP_Control.emergency_monitor_stop(): Monitor already stopped')
                return False
            elif not status['off'] and status['stopping']:
                self._log.out('CHWP_Control.emergency_monitor_stop(): Emergency shutdown in progress')
                return False
            
        with open(os.path.join(this_dir, cg.aux2_status_file), 'wb') as status_file_w:
            status['stopping'] = True
            pkl.dump(status, status_file_w)

        while not status['off']:
            time.sleep(1)
            with open(os.path.join(this_dir, cg.aux2_status_file), 'rb') as status_file:
                status = pkl.load(status_file)

        if self.monitor is not None:
            self.monitor.kill()
            self._log.out('Emergency monitor killed')

        self._log.out('CHWP_Control.emergency_monitor_stop(): Stopping monitor')
        return True

    def slowdaq_publishers_start(self):
        # AUX2 UPS publisher
        if self.pubs['aux2_ups'] is not None:
            self._log.out('aux2_ups publisher already running')
        else:
            self.pubs['aux2_ups'] = subprocess.Popen(['python3', os.path.join(this_dir, '..', 'APC_UPS', 
                                                                              'aux2_ups_pub.py')], 
                                                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self._log.out('aux2 publisher started')
        
        # Cyberswitch publisher
        if self.pubs['cyberswitch'] is not None:
            self._log.out('cyberswitch publisher already running')
        else:
            self.pubs['cyberswitch'] = subprocess.Popen(['python3', os.path.join(this_dir, '..', 'Cyberswitch', 
                                                                                 'cyberswitch_pub.py')], 
                                                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self._log.out('cyberswitch publisher started')
        
        # Gripper publisher
        if self.pubs['gripper'] is not None:
            self._log.out('gripper publisher already running')
        else:
            self.pubs['gripper'] = subprocess.Popen(['python3', os.path.join(this_dir, '..', 'Gripper', 
                                                                             'gripper_pub.py')], 
                                                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self._log.out('gripper publisher started')
        
        # PID publisher
        if self.pubs['pid'] is not None:
            self._log.out('pid publisher already running')
        else:
            self.pubs['pid'] = subprocess.Popen(['python3', os.path.join(this_dir, '..', 'Omega_PID', 
                                                                         'pid_pub.py')], 
                                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self._log.out('pid publisher started')
        
        # PMX publisher
        if self.pubs['pmx'] is not None:
            self._log.out('pmx publisher already running')
        else:
            self.pubs['pmx'] = subprocess.Popen(['python3', os.path.join(this_dir, '..', 'PMX', 'pmx_pub.py')], 
                                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self._log.out('pmx publisher started')
        
        self._log.out('CHWP_Control.slowdaq_publishers_start(): Publishers started')
        return True

    def slowdaq_publishers_stop(self):
        for key in self.pubs.keys():
            if self.pubs[key] is not None:
                self.pubs[key].kill()
                self._log.out(f'{key}: Publisher killed')
        
        self._log.out('CHWP_Control.slowdaq_publishers_stop(): Publishers stopped')
        return True

    # ***** Private Methods *****
    def _rotation_mode(self, mode = 'PID'):
        if mode == 'PID':
            pocc.open_command_close('U')
            self._log.out("CHWP_Control.rotation_mode(): CHWP set to PID control")
            return True
        elif mode == 'VOLT':
            pocc.open_command_close('I')
            self._log.out("CHWP_Control.rotation_mode(): CHWP set to direct voltage control")
            return True
        else:
            self._log.out("ERROR: Invalid mode entered")
            return False

    def _sleep(self, duration=3600.):
        """ Sleep in specified increments """
        granular_time = 60.
        
        for i in range(int(duration / granular_time) + 1):
            time.sleep(granular_time)
        return

    def _squeeze(self, incr=0.1):
        alarm = [False for i in range(3)]
        finished = [False for i in range(3)]
        
        # Iterate through all motors at least once
        while not all(finished):
            for i in range(3):
                try:
                    if not finished[i] or first_pass:
                        alarm[i] = self._push(incr, i + 1)
                        if not alarm[i]:
                            continue
                        elif alarm[i]:
                            gocc.open_command_close('RESET')
                            finished[i] = True
                    else:
                        continue
                except KeyboardInterrupt:
                    self._log.err(
                        "CHWP_Control._squeeze(): User interrupt")
                    return True
        
            first_pass = False
        
        self._log.out("CHWP_Control._squeeze(): Finished squeezing")
        return True
    
    def _push(self, incr, axis):
        """ Push a given axis forward a given amount """
        gocc.open_command_close(f'MOVE PUSH {axis} {incr}')
        result = gocc.open_command_close('ALARM')
        return result

    def _release(self, incr=0.1):
        """ Home the motors """
        return gocc.open_command_close('HOME')

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
                "20s%-10.1f%-10.1f%-10.1f%\n"
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
