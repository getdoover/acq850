import utils 
from enum import Enum
from time import time

#doc: https://library.e.abb.com/public/81bc98f70e8542be8ebdc649bba8b11f/EN_ACQ580_FW_G_A5.pdf?x-sign=wjVUsMpAcVt6qSSSIEjCXsI8niDgFBtEL47buwFnjarqJemywpc2hXu+41V9w2Oc

#ABB Driver Profile p238 of doc
control_word_bits = { 
    'off_1_control':0,
    'off_2_control':1,
    'off_3_control':2,
    'inhibt_operation':3,
    'ramp_out_zero':4,
    'ramp_hold':5,
    'ramp_in_zero':6,
    'reset':7,
    'remote_cmd':10,
    'ext_ctrl_loc':11,
    'user_0':12,
    'user_1':13,
    'user_2':14,
    'user_3':15,
}

#ABB Driver Profile p242 of doc
status_word_bits = {
    'rdy_on':0,
    'rdy_run':1,
    'rdy_ref':2,
    'tripped':3,
    'off_2_status':4,
    'off_3_status':5,
    'swc_on_inhib':6,
    'alarm':7,
    'at_setpoint':8,
    'remote':9,
    'above_limit':10,
    'user_0':11,
    'user_1':12,
    'user_2':13,
    'user_3':14
}


class acq580_states(Enum):
    switch_on_inhibited = 1
    not_ready_to_switch_on = 2
    ready_to_switch_on = 3
    ready_to_operate = 4
    operation_inhibited = 5
    operation_enabled = 6
    output_enabled = 7
    accelerator_enabled = 8
    operation = 9
    off_active = 10


class acq580_state:
    def __init__(self, contactable, register_values, timestamp):
        self.contactable = contactable
        self.register_values = register_values
        self.timestamp = timestamp

    ## Faults
    def check_fault(self):
        sw_bl = self.get_sw_bl() #big endian byte stored in a list
        bit = sw_bl[-4] #counting from 1, the 8th bit is the fault
        if bit == 1:
            return True
        return False
    
    def get_fault_code(self):
        return hex(self.register_values[9])[2:]
    
    ## Warnings
    def check_warning(self):
        sw_bl = self.get_sw_bl()
        bit = sw_bl[-8]
        if bit == 1:
            return True
        return False
    
    def get_warning_code(self):
        return hex(self.register_values[8])[2:]


    #define the checks on the status word



    #off_1_active
    def check_safe_stop(self):
        bit = utils.get_bit_from_bl(self.status_word_bl, 1)
        if bit == 0:
            return True
        return False

    #off_2_active 
    def check_emergency_off(self):
        bit = utils.get_bit_from_bl(self.status_word_bl, 4)
        if bit == 0:
            return True
        return False

    #off_3_active
    def check_emergency_stop(self):
        bit = utils.get_bit_from_bl(self.status_word_bl, 5)
        if bit == 0:
            return True
        return False
    
    def check_switch_on_inhibited(self):
        bit = utils.get_bit_from_bl(self.status_word_bl, 6)
        if bit == 1:
            return True
        return False
    
    def get_sw_int(self):
        return self.register_values[3]
    
    def get_sw_bl(self):
        return utils.int_to_bits(self.get_sw_int())

    def get_cw_int(self):
        return self.register_values[0]
    
    def print_status_word(self):
        utils.rsw(self.get_sw_int())
    
    def print_control_word(self):
        utils.rcw(self.get_cw_int())
    
    def get_motor_rpm(self):
        reg_val = int(self.register_values[101])
        res = (reg_val/65536)*(60000)+(-30000)
        return 
    
    def get_pump_pressure(self):
        raise NotImplementedError
        # read this from the analogue inputs of the drive
        # either 1211 or 1221 depending on how its wired.

        pass

class acq580_state_store:
    def __init__(self) -> None:
        self.states = []
        self.states_length = 100
        pass

    def add_state(self, state):
        self.states.insert(0,state)
        while len(self.states) > self.states_length:
            self.states.pop()

    def get_last(self):
        if len(self.state) < 1:
            return None
        return self.state[0]
    
    def time_in_curr_state(self):
        curr_state = self.get_last().evaluate_state()
        curr_time = time.time()
        dt = 0
        for i in range(0, len(self.states)):
            if self.states[i].evaluate_state() == curr_state:
                dt = curr_time - self.states[i].get_stamp()
            else:
                break
        return dt
    
    def get_previous_state(self):
        state_0 = self.get_state(self)

    def is_initialized(self):
        if len(self.states) > 3:
            return True
        return False
    


    


