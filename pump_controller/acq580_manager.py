from pydoover import ui
from transitions import Machine
import time, asyncio

from acq580_states import *
from utils import *

from pydoover.ui import (
    doover_ui_alert_stream,
    doover_ui_state_command,
    doover_ui_variable,
    doover_ui_action,
    doover_ui_float_parameter,
    doover_ui_element
)

# Define states
states = [
    #standby
    #not-ready to switch on --  initialize
    #read to switch on -- standby
    #running
    #fault

    # stop - stop mode
    # stop OFF1
    # stop OFF2
    # stop OFF3
    
    # fault found
    # warning

    # clearing fault
    'init_state'
    'needs_initializing',
    'not_ready', # idle
    'ready_to_switch_on', #ready to start
    
    'running', # running
    'stopping', 

    # 'stopped', # stopped
    'stopped_off_1',
    'stopped_off_2',
    'stopped_off_3',

    'fault_found',
    'warning_found'
]

transitions = [
    {'trigger': 'state_initialized', 'source': 'init_state', 'dest': 'needs_initializing'},

    #path 1
    {'trigger': 'is_not_ready', 'source':['fault_found','warning_found','needs_initializing', 'stopped_off_1','stopped_off_2','stopped_off_3'], 'dest': 'not_ready'},

    #path 2
    {'trigger': 'is_ready_to_switch_on', 'source': 'needs_initializing', 'dest': 'ready_to_switch_on'},
    {'trigger': 'switch_on', 'source': 'ready_to_switch_on', 'dest': 'running'},
    {'trigger': 'stop', 'source': 'running', 'dest': 'stopping'},
    {'trigger': 'get_ready', 'source': 'stopping', 'dest': 'ready_to_switch_on'},

    {'trigger': 'safe_stop', 'source': '*', 'dest': 'stopped_off_1'},
    {'trigger': 'emergency_off', 'source': '*', 'dest': 'stopped_off_2'},
    {'trigger': 'emergency_stop', 'source': '*', 'dest': 'stopped_off_3'},

    {'trigger': 'fault_detected', 'source': '*', 'dest': 'fault_found'},
    {'trigger': 'reset_fault', 'source': 'fault_found', 'dest': 'not_ready'},

    {'trigger': 'warning_detected', 'source': '*', 'dest': 'warning_found'},

    

    # {'trigger': 'initalize', 'source': ['stopped_off_1','stopped_off_2','stopped_off_3'], 'dest': 'not_ready'},
    # {'trigger': 'get_ready', 'source': 'not_ready', 'dest': 'ready_to_switch_on'},
    # {'trigger': 'start', 'source': 'ready_to_switch_on', 'dest': 'running'},
    # {'trigger': 'stop', 'source': 'running', 'dest': 'stopping'},
    # {'trigger': 'stop_off_1', 'source': 'running', 'dest': 'stopped_off_1'},
    # {'trigger': 'stop_off_2', 'source': 'running', 'dest': 'stopped_off_2'},
    # {'trigger': 'stop_off_3', 'source': 'running', 'dest': 'stopped_off_3'},
    # {'trigger': 'fault_detected', 'source': '*', 'dest': 'fault_found'},
    # {'trigger': 'warning_detected', 'source': '*', 'dest': 'warning'},
    # {'trigger': 'clear_fault', 'source': 'fault_found', 'dest': 'not_ready'},
    # {'trigger': 'clear_warning', 'source': 'warning', 'dest': 'not_ready'}
]

# Define transitions

class acq580_manager:
    def __init__(self, name, disp_name, slave_id, ui_manager, modbus_iface):
        # self.state = 'needs_initializing'
        # self.machine = Machine(model=self, states=states, transitions=transitions, initial='needs_initializing')

        self.name = name
        self.disp_name = disp_name
        self.slave_id = slave_id
        self.ui_manager = ui_manager
        self.modbus_iface = modbus_iface

        #state_store for managing states of acq580
        self.state_store = acq580_state_store()

        self.setup_state_machine()


    def setup_state_machine(self):
        self.s_machine = Machine(model=self, states=states, transitions=transitions, initial='init_state')

    def get_name(self):
        return str(self.name)
    
    def get_ui_manager(self):
        return self.ui_manager

    async def main_loop(self):
        # while True:
        self.spin_state()
        current_state = self.get_sm_state()

        # if self.state_store.is_initialized():
        #     self.

        # big if elif containing all the states and a pass
        if current_state == 'init_state':
            pass
        elif current_state == 'needs_initializing':
            pass

        elif current_state == 'not_ready':
            self.send_get_ready_cw()
            pass

        elif current_state == 'ready_to_switch_on':
            if self.get_start_pump():
                self.send_start_pump_cw()
            pass

        elif current_state == 'running':
            if self.stop_pump():
                print('stop command recieved')
                self.send_stop_pump_cw()
            pass

        elif current_state == 'stopping':
            pass

        elif current_state == 'stopped_off_1':
            pass

        elif current_state == 'stopped_off_2':
            pass

        elif current_state == 'stopped_off_3':
            pass

        elif current_state == 'fault_found':
            pass
        elif current_state == 'warning':
            pass
        else:
            pass

        await asyncio.sleep(0.2)

    def spin_state(self):
        prev_state = None
        current_state = self.get_sm_state()
        self.update_state_store()

        def stop_checks():
            if self.check_emergency_stop():
                self.emergency_stop()

            elif self.check_emergency_off():
                self.emergency_off()

            elif self.check_safe_stop():
                self.safe_stop()

        def fault_checks():
            if self.check_fault():
                self.fault_detected()

            if self.check_warning():
                self.warning_detected()

        while current_state != prev_state:

            acq580_state = self.get_last_acq580_state()
            self.acq580_state_store.add_state(acq580_state)

            prev_state = current_state

            if current_state == 'fault_found':
                if not self.check_fault():
                    self.is_not_ready()
                continue

            elif current_state == 'warning_found':
                if not self.check_warning():
                    self.is_not_ready()
                continue

            else:
                fault_checks()

            if current_state == 'init_state':
                if self.state_store.is_initialized():
                    self.state_initialized()

            elif current_state == 'needs_initializing':
                if self.check_ready_switch_on_sw():
                    self.is_ready_to_switch_on()

                elif self.check_not_ready_sw():
                    self.is_not_ready()

            elif current_state == 'not_ready':
                if self.check_ready_switch_on_sw():
                    self.is_ready_to_switch_on()

            elif current_state == 'ready_to_switch_on':
                stop_checks()
                pass

            elif current_state == 'running':
                stop_checks()
                pass

            elif current_state == 'stopping':
                pass

            elif current_state == 'stopped_off_1':
                if not self.check_safe_stop():
                    self.is_not_ready()
                pass

            elif current_state == 'stopped_off_2':
                if not self.check_emergency_off():
                    self.is_not_ready()
                pass

            elif current_state == 'stopped_off_3':
                if not self.check_emergency_stop():
                    self.is_not_ready()
                pass

            else:
                print('STATE NOT FOUND')
                pass
                
            # self.check_state()
            self.update_state_store()
            time.sleep(0.5)
        


    def fetch_acq580_state(self):
        num_regs = 20
        values = self.modbus_iface.read_registers(
            modbus_id = self.modbus_id,
            start_address = 0,
            num_registers = num_regs,
            slave_id = self.slave_id,
            register_type = 4
        )

        if len(values) < num_regs:
            state = acq580_state(contactable = False, register_values = None, timestamp = time.time())
        else:
            state = acq580_state(contactable = True, register_values = values, timestamp = time.time())
    
    def get_acq580_state(self):
        return self.state_store.get_last()
    
    def update_state_store(self):
        self.state_store.add_state(self.fetch_acq580_state())
    
    def get_pump_rpm(self):
        state = self.get_acq580_state()
        return state.get_pump_rpm()
    
    def get_pump_pressure(self):
        state = self.get_acq580_state()
        return state.get_pump_pressure()
    
    def get_sm_state(self):
        return self.state
    
    def check_not_ready_sw(self):
        # nr_sw = [1,0,0,0,1,1,0,0,0,0]
        # sw = self.get_acq580_state().get_sw_bl()
        # for i in range(-1, -11, -1):
        #     if sw[i] != nr_sw[i]:
        #         return False
        # else :
        #     return True
        sw = self.get_acq580_state().get_sw_bl()
        if sw[-1] is 0:
            return True
        return False
        
    def check_ready_switch_on_sw(self):
        rsw_sw = [1,0,0,0,1,1,0,0,0,1]
        sw = self.get_acq580_state().get_sw_bl()
        for i in range(-1, -11, -1):
            if sw[i] != rsw_sw[i]:
                return False
        else :
            return True

    def get_cw_bl(self):
        return self.acq580_state_store.get_last().get_cw_bl()

    #define the checks on the status word

    #off_1_active
    def check_safe_stop(self):
        if self.acq580_state_store.get_last().check_safe_stop():
            # self.safe_stop()
            return True
        return False

    #off_2_active 
    def check_emergency_off(self):
        if self.state_store.get_last().check_emergency_off():
            # self.emergency_off()
            return True
        return False

    #off_3_active
    def check_emergency_stop(self):
        if self.state_store.get_last().check_emergency_stop():
            # self.emergency_stop()
            return True
        return False
    
    def check_fault(self):
        if self.state_store.get_last().check_fault():
            # self.fault_detected()
            return True
        return False
    
    def get_fault_code(self):
        if self.check_fault():
            res = self.acq580_state_store.get_last().get_fault()
        return None
    
    def get_reset_cw(self):
        #controller needs rising edge on bit 7th (0 indexed) bit to reset fault
        cw_bl = self.get_cw_bl() # big endian
        cw_bl[-8]=1 
        cw_int = utils.bit_list_to_int(cw_bl)
        return utils.bit_list_to_int(cw_bl)
    
    ## Sending Control words
    def _send_cw(self, cw_int):

        res = self.modbus_iface.write_register(
            modbus_id = self.modbus_id,
            slave_id = self.slave_id,
            register_address = 0,
            value = cw_int
        )

        print("control word sent")
        return

    def send_reset_fault(self):
        cw_int = self.get_reset_cw()
        self._send_cw(cw_int)
    
    def send_get_ready_cw(self):
        cw_int = 1150
        self._send_cw(cw_int)

    def send_start_pump_cw(self):
        cw_int = 1151
        self._send_cw(cw_int)

    def send_stop_pump_cw(self):
        cw_int = 1143 # according to param 21.03 in the manual
        self._send_cw(cw_int)
    
    def clear_fault(self):
        action_name  = self.name + "ClearFault"
        
        try:
            self.fault_clearing_sequence()
        except Exception as e:
            self.log_error("Error clearing fault: " + str(e))
            return
        # if successfull:
        self.coerce_command('ClearFault', None)
        return 

    def check_clear_fault_triggered(self):
        action_name  = self.name + "ClearFault"
        cmd = self.get_ui_manager().get_command(action_name)
        if cmd in [True, 'true', 1]:
            return True
        
    def get_start_pump(self):
        action_name  = self.name + "PumpControlMode"
        cmd = self.get_ui_manager().get_command(action_name)
        if cmd == 'start':
            return True
        return False
    
    
    def get_ui_elements(self):
        for pump_manager in self.acq580_pump_controllers:
            # pump_manager.get_ui_elements()
            name = pump_manager.get_name()
            ui_elems = []

            ui_elems.append( doover_ui_alert_stream("significantEvent", "Notify me of any problems") )

            ui_elems.append( 
                doover_ui_variable(
                    name+"PumpRpm",
                    "Pump RPM", 
                    "float", 
                    self.get_pump_rpm(),
                    form="radialGauge",
                    dec_precision=1,
                    ranges=[
                        {
                            "label" : "Low",
                            "min" : 0,
                            "max" : 35,
                            "colour" : 'yellow',
                            "showOnGraph" : True,
                        },
                        {
                            "label" : "Medium",
                            "min" : 35,
                            "max" : 65,
                            "colour" : 'blue',
                            "showOnGraph" : True,
                        },
                        {
                            "label" : "High",
                            "min" : 65,
                            "max" : 100,
                            "colour" : 'green',
                            "showOnGraph" : True,
                        }
                    ],
                )
            )

            ui_elems.append(
                doover_ui_float_parameter(
                    name+"TargetPumpPressure",
                    "Target Pump Pressure (kPa)",
                    float_min = 0,
                    float_max = 300,
                    default_value = 0,
                )
            )

            ui_elems.append(
                doover_ui_state_command(
                    name+"PumpControlMode",
                    "Pump should be:",
                    "select",
                    options=[
                        doover_ui_element('standby', 'Standby'),
                        doover_ui_element('pressure', 'Pressure Mode'),
                        doover_ui_element('rpm', 'RPM Mode'),
                    ],
                    default_value='standby',
                )
            )

            ui_elems.append(
                doover_ui_float_parameter(
                    name + "TargetPumpRpm",
                    "Target Pump RPM",
                    float_min = 0,
                    float_max = 3000,
                    default_value = 0,
                )
            )

            ui_elems.append(
                doover_ui_variable(
                    name+"PumpPressure",
                    "Pump Pressure",
                    "float",
                    pump_manager.get_pump_pressure(),
                    dec_precision=1,
                    form="radialGauge",
                    ranges=[
                        {
                            "label" : "Low",
                            "min" : 0,
                            "max" : 35,
                            "colour" : 'yellow',
                            "showOnGraph" : True,
                        },
                        {
                            "label" : "Medium",
                            "min" : 35,
                            "max" : 65,
                            "colour" : 'blue',
                            "showOnGraph" : True,
                        },
                        {
                            "label" : "High",
                            "min" : 65,
                            "max" : 100,
                            "colour" : 'green',
                            "showOnGraph" : True,
                        }
                    ],
                )
            )

            ## for showing and clearing faults
            ui_elems.append(
                doover_ui_variable(
                    name+"PumpFault",
                    "Fault",
                    "string",
                    pump_manager.get_fault(),
                )
            )

            ui_elems.append(
                doover_ui_action(
                    name+"ClearFault",
                    "Clear Fault",     
                    requires_confirm=True
                )
            )

if __name__ == "__main__":
    drive = DriveController('192.168.1.10')  # Replace with the actual IP address of your drive

    # Example sequence of operations
    drive.start()  # Transition to ready_to_switch_on
    time.sleep(1)  # Wait for the drive to transition
    drive.start()  # Transition to ready_to_operate
    time.sleep(1)  # Wait for the drive to transition
    drive.start()  # Transition to operation_enabled

    # Simulate a fault occurring
    drive.check_fault()

    # Reset fault if it occurred
    if drive.state == 'fault':
        drive.reset_fault()
        time.sleep(1)  # Wait for the drive to reset
        drive.start()  # Restart sequence
