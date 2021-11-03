import sys, os
import time as tm

this_dir = os.path.dirname(__file__)
sys.path.append(
    os.path.join(this_dir, 'src'))
sys.path.append(
    os.path.join(this_dir, '..', 'config'))

import pid_controller as pc
import pb2b_config as cg

pid = pc.PID(cg.pid_ip, cg.pid_port)

if sys.version_info.major == 2:
    print("\nOnly Python 3 supported.")
    print("Usage: sudo python3 pid_command.py [cmd]")
    sys.exit()

def parse_command(command):
    args = command.split(' ')
    cmd = args[0].upper()
    if cmd == 'HELP':
        return _help()
    elif cmd == 'SPIN':
        return _spin(args)
    elif cmd == 'STOP':
        return _stop()
    elif cmd == 'DIR':
        return _dir(args)
    elif cmd == 'FREQ':
        return _freq()
    elif cmd == 'PID':
        return _pid(args)
    elif cmd == 'EXIT':
        sys.exit(0)
    else:
        print('Cannot understand command')
        print("Type 'HELP' for a list of commands")
        return False

def _help():
    print("\n*** PID Controll: Command Menu ***")
    print("HELP = help menu (you're here right now)")
    print('SPIN [freq] = set the pid setpoint to the given frequency')
    print('STOP = set the pid setpoint to 0 Hz and retune the pid parameters')
    print('DIR 0 = set the CHWP to spin in the forward direction')
    print('DIR 1 = set the CHWP to spin in the reverse direction')
    print('FREQ = display the current CHWP frequency')
    print('PID [P] [I] [D] = mannually set the P, I, and D tunning parameters')
    print('EXIT = exit this program\n')
    return True

def _spin(args):
    try:
        freq = float(args[1])
        if freq > 3.5:
            print('Invalid frequency')
            return False
        else:
            pid.declare_freq(freq)
            pid.tune_freq()
            return True
    except:
        print("Cannot understand 'SPIN' argument")
        return False


def _stop():
    pid.tune_stop()
    return True

def _dir(args):
    try:
        pid.set_direction(args[1])
        return True
    except:
        print("Cannot understand 'DIR' argument")
        return False

def _freq():
    print('Current CHWP frequency = {}'.format(pid.get_freq()))
    return True

def _pid(args):
    try:
        pid.set_pid(float(args[1]), float(args[2]), float(args[3]))
        return True
    except:
        print("Cannot understand 'PID' argument")
        return False



if len(sys.argv) > 1:
    command = ''.join(sys.argv[1:])
    while True:
        try:
            parse_command(command)
            sys.exit(0)
        except BlockingIOError:
            print('Busy port, try again!')
else:
    while True:
        command = input("PID command ('HELP' for help): ")
        if command.strip() == '':
            continue
        try:
            parse_command(command)
        except BlockingIOError:
            print('Busy port, try again!')
