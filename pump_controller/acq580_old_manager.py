
states = [
    'initalizing',
    'switch_on_inhibited',
    'not_ready_to_switch_on',
    'ready_to_switch_on',
    'ready_to_operate',
    'operation_inhibited',
    'operation_enabled',
    'output_enabled',
    'accelerator_enabled',
    'operation',
    'operation_inhibited',
    'off_1_active',
    'off_2_active',
    'off_3_active',
    'fault'
]


transitions = [
    # initializing
    {'trigger': 'initalized', 'source': 'initializing', 'dest': 'not_ready_to_switch_on'},

    # off_1_active
    {'trigger': 'safe_stop', 'source': '*', 'dest': 'off_1_active'},

    # off_2_active
    {'trigger': 'emergency_off', 'source': '*', 'dest': 'off_2_active'},
    
    # off_3_active
    {'trigger': 'emergency_stop', 'source': '*', 'dest': 'off_3_active'},

    # fault
    {'trigger': 'fault_detected', 'source': '*', 'dest': 'fault'},

    # switch_on_inhibited
    {'trigger': 'init_switch_on', 'source': ['off_1_active', 'off_2_active', 'off_3_active'], 'dest': 'switch_on_inhibited'},

    # not_ready_to_switch_on 
    {'trigger': 'enable_switch_on', 'source': ['switch_on_inhibited', 'off_1_active'], 'dest': 'not_ready_to_switch_on'}, # triggered by user

    # ready_to_switch_on
    {'trigger': 'ready_switch_on', 'source': 'not_ready_to_switch_on', 'dest': 'ready_to_switch_on'},

    # ready_to_operate
    {'trigger': 'init_operation', 'source': ['ready_to_switch_on', 'operation_inhibited'], 'dest': 'ready_to_operate'},

    # operation_enabled
    {'trigger': 'enable_operatation', 'source': 'ready_to_operate', 'dest': 'operation_enabled'},

    # output_enabled
    {'trigger': 'enable_output', 'source': 'operation_enabled', 'dest': 'output_enabled'},

    # accelerator_enabled
    {'trigger': 'enable_accelerator', 'source': 'output_enabled', 'dest': 'accelerator_enabled'},

    # operation
    {'trigger': 'operate', 'source': 'accelerator_enabled', 'dest': 'operation' }
]

def spin_state(self):
    prev_state = None
    current_state = self.get_sm_state()
    acq580_state
    self.acq580_state_store.add_state(acq580_state)

    while current_state != prev_state:

        acq580_state = self.get_last_acq580_state()
        self.acq580_state_store.add_state(acq580_state)

        if self.check_fault():
            self.fault_detected()

        prev_state = current_state
        
        if current_state == 'initializing':
            if len(self.acq580_state_store) < 3:
                continue
            else:
                if acq580_state.check_emergency_stop():
                    self.emergency_stop()

                elif acq580_state.check_emergency_off():
                    self.emergency_off()

                elif acq580_state.check_fault():
                    self.fault_detected()

                elif acq580_state.check_safe_stop():
                    self.safe_stop()

                else:
                    self.initialized()
        
        if state == 'fault':
            self.set_fault(self.get_faults())
            if self.check_clear_fault_triggered():
                self.clear_fault()
            # if self.check_fault():
            #     self.fault_detected()
            
        self.check_state()
        time.sleep(1)