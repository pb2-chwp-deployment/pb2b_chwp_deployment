import sys, os

this_dir = os.path.dirname(__file__)
sys.path.append(
        os.path.join(this_dir, '..', '..', 'config'))
sys.path.append(this_dir)

import NP05B as np
import pb2b_config as cg
import command_NP05B as cm
import fcntl as f

def open_command_close(cmd):
    lockfile = open('.port_busy')
    f.flock(lockfile, f.LOCK_EX | f.LOCK_NB)
    NP05B = np.NP05B(tcp_ip=cg.cyberswitch_tcp_ip, tcp_port=cg.cyberswitch_tcp_port)
    CMD = cm.Command(NP05B)
    result = CMD.CMD(cmd)
    del(NP05B,CMD)
    f.flock(lockfile, f.LOCK_UN)
    return result
