#!/usr/bin/python3

# Built-in python modules
import sys as sy
import argparse as ap
import os

# CHWP control modules
this_dir = os.path.dirname(__file__)
sy.path.append(
    os.path.join(this_dir, 'src'))
import chwp_control as cc  # noqa: E402

def print_help():
    print('\n*** PB2b CHWP Control: Commands ***')
    print('warm_grip: Grip the CHWP rotor when the crystat is warm')
    print('cooldown_grip: ')
    print('cold_grip: Grip the CHWP rotor when the crystat is cold')
    print('gripper_home: Send all grippers to their home positions')
    print('gripper_reboot: Cycle power to the gripper controller')
    print('rotation_direction [-d]: Set the CHWP rotation direction: True = Forward, False = Reverse')
    print('rotation_stop: Use PID to stop the CHWP rotation')
    print('rotation_spin [-f]: Use PID to rotate CHWP at provided frequency [0.0 - 3.0]')
    print('rotation_voltage [-v]: Set the drive voltage to a specific value [0.0 - 36.0]')
    print('rotation_off: Turn off drive voltage power supply')
    print('bb_packet_collect: Start process on Beaglebones to generate encoder packets')
    print('start_emergency_monitor: Start emergency stop monitor')
    print('stop_emergency_monitor: Stop emergenct stop monitor')
    print('start_slowdaq_publishers: Start all CHWP slowdaq publishers')
    print("help: Help menu (you're here now)")

CC = cc.CHWP_Control()
# Allowed command line arguments
cmds = {'warm_grip': CC.warm_grip,
        'cooldown_grip': CC.cooldown_grip,
        'cold_grip': CC.cold_grip,
        'cold_ungrip': CC.cold_ungrip,
        'gripper_home': CC.gripper_home,
        'gripper_reboot': CC.gripper_reboot,
        'rotation_direction': CC.rotation_direction,
        'rotation_stop': CC.rotation_stop,
        'rotation_spin': CC.rotation_spin,
        'rotation_voltage': CC.rotation_voltage,
        'rotation_off': CC.rotation_off,
        'bb_packet_collect': CC.bb_packet_collect,
        'start_emergency_monitor': CC.start_emergency_monitor,
        'stop_emergency_monitor': CC.stop_emergency_monitor,
        'start_slowdaq_publishers': CC.start_slowdaq_publishers,
        'help', print_help}

ps = ap.ArgumentParser(
    description="Control program for the PB2bc CHWP")
ps.add_argument('command', choices=cmds.keys())
ps.add_argument('-d', action = 'store', dest = 'direction', type = bool, default = True)
ps.add_argument('-f', action = 'store', dest = 'frequency', type = float, default = 0.0)
ps.add_argument('-v', action = 'store', dest = 'voltage', type = float, default = 0.0)

args = ps.parse_args()
func = cmds[args.command]

if func == CC.rotation_direction:
    func(args.direction)
elif func == CC.rotation_spin:
    func(args.frequency)
elif func == CC.rotation_voltage:
    func(args.voltage)
else:
    func()
