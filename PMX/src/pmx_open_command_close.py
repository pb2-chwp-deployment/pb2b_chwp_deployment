import sys, os, time

this_dir = os.path.dirname(__file__)
sys.path.append(
    os.path.join(this_dir, '..', '..', 'config'))
sys.path.append(this_dir)

import pmx as pm
import pb2b_config as cg
import command as cm
import fcntl as f

def open_command_close(cmd, ip = cg.kdrive_ip, port = cg.kdrive_port, 
		       lock = '.drive_port_busy'):
    while True:
        try:
            lockfile = open(os.path.join(this_dir, lock))
            f.flock(lockfile, f.LOCK_EX | f.LOCK_NB)
            break
        except BlockingIOError:
            print('PMX BlockingIOError, trying again')
            time.sleep(1)

    PMX = pm.PMX(tcp_ip=ip, tcp_port=port)
    CMD = cm.Command(PMX)
    result = CMD.user_input(cmd)
    del(PMX,CMD)
    f.flock(lockfile, f.LOCK_UN)
    return result
