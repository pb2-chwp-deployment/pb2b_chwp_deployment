#Built-in python modules
import time as tm
import serial as sr
import sys as sy
import os

# CHWP control modules
this_dir = os.path.dirname(__file__)
sy.path.append(this_dir)
sy.path.append(
    os.path.join(this_dir, '..', '..',  "config"))
sy.path.append(
    os.path.join(this_dir, '..', '..', 'MOXA'))

import pb2b_config as cg  # noqa: E402
import log_NP05B as lg  # noqa: E402
import moxaSerial as mx  # noqa: E402

class NP05B:
    """
    The NP_05B object for communicating with the Synaccess Cyberswitch

    Args:
    rtu_port (int): Modbus serial port (defualt None).
    tcp_ip (str): TCP IP address (default None)
    tcp_port (int): TCP IP port (default None)

    Only either rtu_port or tcp_ip + tcp_port can be defined.
    """
    def __init__(self, rtu_port=None, tcp_ip=None, tcp_port=None):
        # Logging object
        self.log = lg.Logging()

        # Connect to device
        if rtu_port is None and tcp_ip is None and tcp_port is None:
            if cg.use_tcp:
                self.__conn(tcp_ip=cg.cyberswitch_tcp_ip, tcp_port=cg.cyberswitch_tcp_port)
            else:
                self.__conn(rtu_port=cg.rtu_port)
        else:
            self.__conn(rtu_port, tcp_ip, tcp_port)

        # Read parameters
        self._num_tries = 1
        self._bytes_to_read = 20
        self._tstep = 0.2

    def __del__(self):
        if not cg.use_tcp:
            self.log.log(
                "Closing RTU serial connection at port %s"
                % (cg.rtu_port))
            self._clean_serial()
            self._ser.close()
            #print("Deconstructor called")
        else:
            self.log.log(
                "Closing TCP connection at IP %s and port %s"
                % (self._tcp_ip, self._tcp_port))
            pass
        return

    def ON(self, port):
        """ Power on a specific port """
        cmd = b'$A3 %d 1' % (port)
        self._command(cmd)
        return True

    def OFF(self, port):
        """ Power off a specific port """
        cmd = b'$A3 %d 0' % (port)
        self._command(cmd)
        return True

    def ALL_ON(self):
        """ Power on all ports """
        cmd = b'$A7 1'
        self._command(cmd)
        return True

    def ALL_OFF(self):
        """ Power off all ports """
        cmd = b'$A7 0'
        self._command(cmd)
        return True

    def REBOOT(self, port):
        """ Reboot a specific port """
        cmd = b'$A4 %d' % (port)
        self._command(cmd)
        return True

    def STATUS(self):
        """ Print the power status for all ports """
        cmd = b'$A5'
        for n in range(self._num_tries):
            self._write(cmd)
            out = self._read()
            if len(out) == 0:
                continue
            elif len(out) != 0:
                stat = out[1].decode().replace("\x00", '').replace(",", '').replace("$A0", '').replace("\n", '').replace("\r", '').replace("$A5", '')
                return list(stat)[::-1]
            else:
                self.log.err(
                    "Did not understand NP_05B output %s" % (out))
                continue
        return True

    # ***** Helper methods *****
    def __conn(self, rtu_port=None, tcp_ip=None, tcp_port=None):
        """ Connect to device either via TCP or RTU """
        if rtu_port is None and (tcp_ip is None or tcp_port is None):
            raise Exception('NP_05B Exception: no RTU or TCP port specified')
        elif (rtu_port is not None and
              (tcp_ip is not None or tcp_port is not None)):
            raise Exception(
                "NP_05B Exception: RTU and TCP port specified. "
                "Can only have one or the other.")
        elif rtu_port is not None:
            self._ser = sr.Serial(
                port=rtu_port, baudrate=9600, bytesize=8,
                parity='N', stopbits=1, timeout=1)
            self.log.log(
                "Connecting to RTU serial port %s" % (rtu_port))
            cg.use_tcp = False
            cg.rtu_port = rtu_port
        elif tcp_ip is not None and tcp_port is not None:
            self._ser = mx.Serial_TCPServer((tcp_ip, tcp_port))
            self.log.log(
                "Connecting to TCP IP %s via port %d"
                % (tcp_ip, int(tcp_port)))
            cg.use_tcp = True
            self._tcp_ip = tcp_ip
            self._tcp_port = tcp_port

    def _wait(self):
        """ Wait a specific timestep """
        tm.sleep(self._tstep)
        return True

    def _clean_serial(self):
        """ Flush the serial buffer """
        if not cg.use_tcp:
            self._ser.reset_input_buffer()
            self._ser.reset_output_buffer()
            self._ser.flush()
        else:
            self._ser.flushInput()
        return

    def _write(self, cmd):
        """ Write to the serial port """
        self._clean_serial()
        self._ser.write((cmd+b'\r'))
        self._wait()

    def _read(self):
        """ Read from the serial port """
        if not cg.use_tcp:
            return self._ser.readlines()
        else:
            raw_out = self._ser.read(self._bytes_to_read)
            out = raw_out.replace(b'\r', b' ').replace(b'\x00', b'')
            return out.split(b' ')

    def check_output(self, cmd):
        """ Check the output """
        out = self._read()
        if len(out) == 0:
            return False
        elif cmd.decode() in out[0].decode() and '$A0' in out[1].decode():
            return True
        elif not len([s for s in out if b'Telnet active.' in s]) == 0:
            self.log.log('Telnet active. Resetting... try command again.')
            return self._deactivate_telnet()
        else:
            self.log.err(
                    "Did not understand NP_05B output %s" % (out))
            return False

    def _command(self, cmd):
        """ Send a command to the device """
        for n in range(self._num_tries):
            self._write(cmd)
            #result = self.check_output(cmd)
            #if result:
                #return True
            #else:
                #continue
        return True

    def _deactivate_telnet(self):
        """ Attempt to deactivate Telnet session to the device """
        self.log.log("Telnet session active! Trying to deactivate...")
        cmd = b'!'
        self._write(cmd)
        out = self._ser.readlines()[0]
        if cmd in out:
            return True
        else:
            self.log.err(
                    "Did not understand NP_05B output %s" % (out))
            return False
