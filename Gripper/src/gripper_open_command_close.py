import sys, os

this_dir = os.path.dirname(__file__)
sys.path.append(
    os.path.join(this_dir, 'src'))
sys.path.append(
    os.path.join(this_dir, '..', '..', 'config'))

import pb2b_config as cg
import C000DRD as c0
import JXC831 as jx
import control as ct
import gripper as gp
import command_gripper as cd
import fcntl as f

def open_command_close(cmd):
    lockfile = open('.port_busy')
    f.flock(lockfile, f.LOCK_EX | f.LOCK_NB)
    if cg.use_tcp:
        PLC = c0.C000DRD(tcp_ip=cg.gripper_ip, tcp_port=cg.gripper_port)
    else:
        PLC = c0.C000DRD(rtu_port=cg.rtu_port)
#    print('Port opened')
    JXC = jx.JXC831(PLC)
    CTL = ct.Control(JXC)
    GPR = gp.Gripper(CTL)
    CMD = cd.Command(GPR)
    result = CMD.CMD(cmd)
#    print('Command sent')
#    print('Port closed')
    del(PLC,JXC,CTL,GPR,CMD)
    f.flock(lockfile, f.LOCK_UN)
    return result
