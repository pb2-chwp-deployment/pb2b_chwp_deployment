from easysnmp import Session
import os
import fcntl
import time

this_dir = os.path.dirname(__file__)

class UPS:
    def __init__(self, host_ip, lock_file_name = os.path.join(this_dir, '.aux2_port_busy')):
        self.HOST = host_ip
        self.USER = 'PCBEUser'
        self.snmp_version = 1
        self.lock_file_name = lock_file_name

        self.session = Session(hostname=self.HOST, community=self.USER, 
                               version=self.snmp_version)

        self.oid_names()
        self.update()

    def oid_names(self):
        self.batt_capacity_oid = 'iso.3.6.1.4.1.318.1.1.1.2.2.1.0'
        self.input_voltage_oid = 'iso.3.6.1.4.1.318.1.1.1.3.2.1.0'
        self.input_freq_oid = 'iso.3.6.1.4.1.318.1.1.1.3.2.4.0'
        self.output_status_oid = 'iso.3.6.1.4.1.318.1.1.1.4.1.1.0'
        self.output_voltage_oid = 'iso.3.6.1.4.1.318.1.1.1.4.2.1.0'
        self.output_freq_oid = 'iso.3.6.1.4.1.318.1.1.1.4.2.2.0'
        self.output_load_oid = 'iso.3.6.1.4.1.318.1.1.1.4.2.3.0'

    def update(self):
        while True:
            try:
                self.lock_file = open(self.lock_file_name)
                fcntl.flock(self.lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except BlockingIOError:
                time.sleep(0.1)

        self.input_cable()
        self.battery_charge()
        self.output_cable()

    def input_cable(self):
        self.input_voltage = self.session.get(self.input_voltage_oid).value
        self.input_freq = self.session.get(self.input_freq_oid).value

    def battery_charge(self):
        self.batt_capacity = self.session.get(self.batt_capacity_oid).value

    def output_cable(self):
        self.output_status = self.session.get(self.output_status_oid).value
        self.output_voltage = self.session.get(self.output_voltage_oid).value
        self.output_freq = self.session.get(self.output_freq_oid).value
        self.output_load = self.session.get(self.output_load_oid).value


if __name__ == '__main__':
    CHWP_UPS = UPS('192.168.2.59')
    print('Output Status:', CHWP_UPS.output_status)
    print('Output Voltage:', CHWP_UPS.output_voltage,'V')
    print('Output Frequency:', CHWP_UPS.output_freq,'Hz')
    print('Output Load:', CHWP_UPS.output_load,'%')
    print('Input Voltage:', CHWP_UPS.input_voltage,'V')
    print('Input frequency:', CHWP_UPS.input_freq,'Hz')
    print('Battery Percentage:', CHWP_UPS.batt_capacity,'%')
