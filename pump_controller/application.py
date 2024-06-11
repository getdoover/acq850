import asyncio
import time

from acq580_manager import acq580_manager

from pydoover.docker import app_base, run_app
from pydoover.ui import *


class log_manager:

    def __init__(self, min_period_secs):

        self.min_period_secs = min_period_secs
        self.last_critical_values = {}
        self.log_required = True
        self.last_log_time = time.time()

    def set_min_period_secs(self, min_period):
        self.min_period_secs = min_period

    def add_critical_value(self, name, value):
        if name in list(self.last_critical_values.keys()):
            last_val = self.last_critical_values[name]
            if last_val != value:
                print("Recorded different critical value : " + str(name) + " = " + str(value))
                self.log_required = True
        else:
            self.log_required = True

        self.last_critical_values[name] = value

    def record_log_sent(self):
        self.log_required = False
        self.last_log_time = time.time()

    def is_log_required(self):
        if self.log_required:
            return True
        if time.time() - self.last_log_time > self.min_period_secs:
            return True

        return False


class Application(app_base):
    def setup(self):
        super.setup()

        self.pump_control_options = [
            doover_ui_element('standby', 'Standby'),
            doover_ui_element('pressure', 'Pressure Mode'),
            doover_ui_element('rpm', 'RPM Mode'),
        ]

        self.main_loop_sleep_time = 1
        config_manager = self.config_manager

        self.acq580_pump_controllers = []
        self.acq580_settings = config_manager.get_config('ACQ580_SETTINGS')
        if self.acq580_settings is None:
            self.acq580_settings = [
                acq580_manager(
                    name='ACQ580_Tester',
                    disp_name='ACQ580 1',
                    slave_id=10,
                    ui_manager=self.get_ui_manager(),
                    modbus_iface=self.get_modbus_iface()
                )
            ]
        # else:
        #     for acq580_setting in self.acq580_settings:
        self.doover_log_manager = log_manager(self.comms_low_rate_send_interval)


    def main_loop(self):

        if not self.get_ui_manager().get_has_been_connected():
            print("Cycling - Waiting to ensure connectivity to the cloud")
            for acq580 in self.acq580_pump_controllers:
                self.get_ui_manager().set_children(acq580.get_ui_elements())
                self.get_ui_manager().get_update()

            time.sleep(1)
        else:
            print("Iterating...")
            print("Last loop = " + str(time.time() - self.last_loop_start) + " seconds")
            self.last_loop_start = time.time()

    # define ui in ui components
    


        # return self.acq580_pump_controllers

    if __name__ == "__main__":
        run_app(Application())
