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
    print('warm_grip:                   Grip the CHWP rotor when the crystat is warm')
    print('cooldown_grip:               Periodically grip the CHWP rotor as the cryostat cools down')
    print('cold_grip:                   Grip the CHWP rotor when the crystat is cold')
    print('gripper_home:                Send all grippers to their home positions')
    print('gripper_alarm:               Prints the current gripper alarm state')
    print('gripper_reset:               Attempt to reset the current gripper alarm')
    print('gripper_reboot:              Cycle power to the gripper controller')
    print("rotation_bias [value]:       Turn on/off biasing power supplies: ['on' or 'off']")
    print("rotation_direction [value]:  Set the CHWP rotation direction: ['forward' or 'reverse']")
    print('rotation_status:             Print status of the PID controller and PMX power supply')
    print('rotation_stop:               Use PID to stop the CHWP rotation')
    print('rotation_spin [value]:       Use PID to rotate CHWP at provided frequency [0.0 - 3.0]')
    print('rotation_voltage [value]:    Set the drive voltage to a specific value [0.0 - 36.0]')
    print('rotation_off:                Turn off drive voltage power supply')
    print('bb_packet_collect:           Start process on Beaglebones to generate encoder packets')
    print('start_emergency_monitor:     Start emergency stop monitor')
    print('stop_emergency_monitor:      Stop emergenct stop monitor')
    print('start_slowdaq_publishers:    Start all CHWP slowdaq publishers')
    print('stop_slowdaq_publishers:     Stop all CHWP slowdaq publishers')
    print("help:                        Help menu (you're here now)")
    print('exit:                        Exit')

def exit():
    sy.exit(0)

def process_command(user_input):
    args = user_input.split(' ')
    cmd = args[0].lower()
    if cmd not in cmds.keys():
        print("Cannot understand command")
        print("Type 'help' for a list of commands.")
        return

    func = cmds[cmd]
    if func == CC.rotation_direction:
        func(str(args[1]))
    elif func == CC.rotation_spin:
        func(float(args[1]))
    elif func == CC.rotation_voltage:
        func(float(args[1]))
    elif func == CC.rotation_bias:
        func(str(args[1]))
    else:
        func()
    print()

CC = cc.CHWP_Control()
# Allowed command line arguments
cmds = {'warm_grip': CC.warm_grip,
        'cooldown_grip': CC.cooldown_grip,
        'cold_grip': CC.cold_grip,
        'cold_ungrip': CC.cold_ungrip,
        'gripper_home': CC.gripper_home,
        'gripper_alarm': CC.gripper_alarm,
        'gripper_reset': CC.gripper_reset,
        'gripper_reboot': CC.gripper_reboot,
        'rotation_bias': CC.rotation_bias,
        'rotation_direction': CC.rotation_direction,
        'rotation_status': CC.rotation_status,
        'rotation_stop': CC.rotation_stop,
        'rotation_spin': CC.rotation_spin,
        'rotation_voltage': CC.rotation_voltage,
        'rotation_off': CC.rotation_off,
        'bb_packet_collect': CC.bb_packet_collect,
        'start_emergency_monitor': CC.start_emergency_monitor,
        'stop_emergency_monitor': CC.stop_emergency_monitor,
        'start_slowdaq_publishers': CC.start_slowdaq_publishers,
        'stop_slowdaq_publishers': CC.stop_slowdaq_publishers,
        'help': print_help,
        'exit': exit}

ps = ap.ArgumentParser(
    description="Control program for the PB2b CHWP")
ps.add_argument('-c', action = 'store', dest = 'command', choices=cmds.keys())
ps.add_argument('-d', action = 'store', dest = 'direction', type = str, default = 'forward')
ps.add_argument('-f', action = 'store', dest = 'frequency', type = float, default = 0.0)
ps.add_argument('-v', action = 'store', dest = 'voltage', type = float, default = 0.0)
ps.add_argument('-p', action = 'store', dest = 'power', type = str, default = 'off')

args = ps.parse_args()
if len(sy.argv) > 1:
    func = cmds[args.command]

    if func == CC.rotation_direction:
        func(args.direction)
    elif func == CC.rotation_spin:
        func(args.frequency)
    elif func == CC.rotation_voltage:
        func(args.voltage)
    elif func == CC.rotation_bias:
        func(args.power)
    else:
        func()
else:
    while True:
        command = input("CHWP command ('help' for help): ")
        if command.strip() == '':
            continue
        process_command(command)
