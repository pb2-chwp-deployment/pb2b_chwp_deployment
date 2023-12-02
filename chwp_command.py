#!/usr/bin/python3

# Built-in python modules
import sys
import argparse
import os

# CHWP control modules
this_dir = os.path.dirname(__file__)
sys.path.append(
    os.path.join(this_dir, 'src'))
import chwp_control as cc  # noqa: E402

def print_help():
    print('\n*** PB2b CHWP Control: Commands ***')
    print('warm_grip:                           Grip the CHWP rotor when the cryostat is warm')
    print('cooldown_grip:                       Periodically grip the CHWP rotor as the cryostat cools down')
    print('cold_grip:                           Grip the CHWP rotor when the cryostat is cold')
    print('gripper_home:                        Send all grippers to their home positions')
    print("gripper_brake [value]:               Turn on/off the gripper brakes: ['on' or 'off']")
    print('gripper_alarm:                       Prints the current gripper alarm state')
    print('gripper_reset:                       Attempt to reset the current gripper alarm')
    print('gripper_reboot:                      Cycle power to the gripper controller')
    print("rotation_bias [value]:               Turn on/off biasing power supplies: ['on' or 'off']")
    print("rotation_direction [value]:          Set the CHWP rotation direction: ['forward' or 'reverse']")
    print('rotation_status:                     Print status of the PID controller and PMX power supply')
    print('rotation_stop:                       Use PID to stop the CHWP rotation')
    print('rotation_spin [value]:               Use PID to rotate CHWP at provided frequency: [0.0 - 3.0]')
    print('rotation_voltage [value]:            Set the drive voltage to a specific value: [0.0 - 36.0]')
    print('rotation_off:                        Turn off drive voltage power supply')
    print("bb_reboot [value]:                   Reboot Beaglebones: [(optional) index '1' or '2']")
    print("bb_packet_collect_start [value]:     Start process on Beaglebones to generate encoder packets:")
    print("                                     [(optional) index '1' or '2']")
    print('bb_packet_collect_stop:              Stop process on Beaglebones generating encoder packets')
    print("emergency_monitor_start [value]:     Start emergency stop monitor: [(optional) verbose '0' or '1']")
    print('emergency_monitor_stop:              Stop emergency stop monitor')
    print('slowdaq_publishers_start:            Start all CHWP slowdaq publishers')
    print('slowdaq_publishers_stop:             Stop all CHWP slowdaq publishers')
    print("help:                                Help menu (you're here now)")
    print('exit:                                Exit')

def exit():
    CC.__exit__()
    sys.exit(0)

def process_command(user_input):
    args = user_input.split(' ')
    cmd = args[0].lower()
    if cmd not in cmds.keys():
        print("Cannot understand command")
        print("Type 'help' for a list of commands.")
        return

    func = cmds[cmd]
    if func in [CC.rotation_direction, CC.rotation_bias, CC.gripper_brake]:
        func(str(args[1]))
    elif func in [CC.rotation_spin, CC.rotation_voltage]:
        func(float(args[1]))
    elif func == CC.emergency_monitor_start:
        if len(args) > 1:
            func(verb = args[1])
        else:
            func()
    elif func in [CC.bb_packet_collect_start, CC.bb_reboot]:
        if len(args) > 1:
            func(index = int(args[1]))
        else:
            func()
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
        'gripper_brake': CC.gripper_brake,
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
        'bb_reboot': CC.bb_reboot,
        'bb_packet_collect_start': CC.bb_packet_collect_start,
        'bb_packet_collect_stop': CC.bb_packet_collect_stop,
        'emergency_monitor_start': CC.emergency_monitor_start,
        'emergency_monitor_stop': CC.emergency_monitor_stop,
        'slowdaq_publishers_start': CC.slowdaq_publishers_start,
        'slowdaq_publishers_stop': CC.slowdaq_publishers_stop,
        'help': print_help,
        'exit': exit}

ps = argparse.ArgumentParser(
    description="Control program for the PB2b CHWP")
ps.add_argument('-c', action = 'store', dest = 'command', choices=cmds.keys())
ps.add_argument('-d', action = 'store', dest = 'direction', type = str, default = 'forward')
ps.add_argument('-f', action = 'store', dest = 'frequency', type = float, default = 0.0)
ps.add_argument('-v', action = 'store', dest = 'voltage', type = float, default = 0.0)
ps.add_argument('-p', action = 'store', dest = 'power', type = str, default = 'off')

args = ps.parse_args()
if len(sys.argv) > 1:
    func = cmds[args.command]

    if func == CC.rotation_direction:
        func(direction = args.direction)
    elif func == CC.rotation_spin:
        func(frequency = args.frequency, set_dir = False)
    elif func == CC.rotation_voltage:
        func(voltage = args.voltage, set_dir = False)
    elif func == CC.rotation_bias:
        func(power = args.power)
    else:
        func()
else:
    while True:
        try:
            command = input("CHWP command ('help' for help): ")
            if command.strip() == '':
                continue
            process_command(command)
        except KeyboardInterrupt:
            process_command('exit')
