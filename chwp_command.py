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
        'roation_voltage': CC.rotation_voltage,
        'rotation_off': CC.roation_off,
        'bb_packet_collect': CC.bb_packet_collect,
        'start_emergency_monitor': CC.start_emergency_monitor,
        'stop_emergency_monitor': CC.stop_emergency_monitor}

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
