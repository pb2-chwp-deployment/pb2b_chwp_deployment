import sys, os

class PID_Command:
    def __init__(self, PID=None):
        if PID is None:
            raise Exception(
                'Command error: No pid object passed '
                'to PID_Command() constructor')

        else
            self.PID = PID

    def CMD(self, user_input):
        args = user_input.split(' ')
        cmd = args[0].upper()
        if cmd == 'HELP':
            return self._help()
        elif cmd == 'STOP':
            return self._stop()
        elif cmd == 'SPIN':
            return self._spin(args)
        elif cmd == 'DIR':
            return self._dir(args)
        elif cmd == 'GFREQ':
            return self.PID.get_freq()
        elif cmd == 'EXIT':
            sys.exit(0)
        else:
            print("Cannont understand command '%s'." % cmd)
            print("Type 'HELP' for a list of commands.")

    def _help(self):
        print("\n*** PID Control: Command Menu ***")
        print("HELP = help menu (you're here right now)")
        print("STOP = stop the chwp rotation")
        print("SPIN [freq] = spin the chwp to [freq]")
        print("DIR 0 = set the chwp to forward")
        print("DIR 1 = set the chwp to reverse")
        print("GFREQ = display the current chwp frequency")
        print("EXIT = exit the program\n")
        return True

    def _stop(self):
        pass

    def _spin(self, args):
        freq = args[1]
        if self.PID.forward:
            self.PID.set_direction('0')
        else:
            self.PID.set_direction('1')

        self.PID.declare_freq(freq)
        self.PID.tune_freq()

    def _dir(self, args):
        direction = args[1]
        if direction == '0' or direction == '1'
            self.PID.set_direction(direction)
        else:
            print("Unable to parse direction")
            return False
