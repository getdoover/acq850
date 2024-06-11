# Description: This file contains utility functions that are used in the main program.

def bytes_to_bits(byte):
    bits = [int(i) for i in "{0:08b}".format(byte)]
    while len(bits) % 4 != 0:
        bits.insert(0,0)
    return bits

def bit_list_to_int(bit_list):
    res = int("".join(str(x) for x in bit_list), 2)
    res = ""
    for i in bit_list:
        res += str(i)
        print(res)
    return int(res, 2)

def byte_string_to_bits(byte_string):
    res = []
    for byte in byte_string:
        res.extend(bytes_to_bits(byte))
    return res

def hex_string_to_bits(hex_string):
    return byte_string_to_bits(bytearray.fromhex(hex_string))

def int_to_bits(num):
    if num is None:
        return None
    b_a = num.to_bytes(2, byteorder='big')
    return byte_string_to_bits(b_a)

def get_bit_from_bl(bit_list, bit_index):
    if bit_index > ( len(bit_list) - 1 ):
        return None
    index = (bit_index * -1)-1
    return bit_list[index]

def bit_nums():
    return [5, 4, 3, 2, 1, 0, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0]

def rsw(sw, sw1 = None): #read control word
    swb = int_to_bits(sw)
    if sw1 is None:
        swb1 = [None]*16
    else:
        swb1 = int_to_bits(sw1)
    # iterate through bit_list in reverse order
    status_word_description = f'''
        Bit 0 : Ready to switch ON  = {swb[-1]} {swb1[-1]}
        Bit 1 :          Ready run  = {swb[-2]} {swb1[-2]}
        Bit 2 :          Ready ref  = {swb[-3]} {swb1[-3]}
        Bit 3 :           Tripped   = {swb[-4]} {swb1[-4]}
        Bit 4 :    Off 2 inactive   = {swb[-5]} {swb1[-5]}
        Bit 5 :    Off 3 inactive   = {swb[-6]} {swb1[-6]}
        Bit 6 : Switch-on inhibited = {swb[-7]} {swb1[-7]}
        Bit 7 :           Warning   = {swb[-8]} {swb1[-8]}
        Bit 8 :        At setpoint  = {swb[-9]} {swb1[-9]}
        Bit 9 :            Remote   = {swb[-10]} {swb1[-10]}
        Bit 10:       Above limit   = {swb[-11]} {swb1[-11]}
        Bit 11:        User bit 0   = {swb[-12]} {swb1[-12]}
        Bit 12:        User bit 1   = {swb[-13]} {swb1[-13]}
        Bit 13:        User bit 2   = {swb[-14]} {swb1[-14]}
        Bit 14:        User bit 3   = {swb[-15]} {swb1[-15]}
        Bit 15:          Reserved   = {swb[-16]} {swb1[-16]}
    '''
    print(status_word_description)
    return

def rcw(cw, cw1 = None):
    cwb = int_to_bits(cw)
    if cw1 is None:
        cwb1 = [None]*16
    else:
        cwb1 = int_to_bits(cw1)
    # iterate through bit_list in reverse order
    control_word_description = f'''
        Bit  0 :      OFF1_CONTROL  = {cwb[-1]} {cwb1[-1]}
        Bit  1 :      OFF2_CONTROL  = {cwb[-2]} {cwb1[-2]}
        Bit  2 :      OFF3_CONTROL  = {cwb[-3]} {cwb1[-3]}
        Bit  3 : INHIBIT_OPERATION  = {cwb[-4]} {cwb1[-4]}
        Bit  4 :     RAMP_OUT_ZERO  = {cwb[-5]} {cwb1[-5]}
        Bit  5 :         RAMP_HOLD  = {cwb[-6]} {cwb1[-6]}
        Bit  6 :      RAMP_IN_ZERO  = {cwb[-7]} {cwb1[-7]}
        Bit  7 :             RESET  = {cwb[-8]} {cwb1[-8]}
        Bit  8 :          Reserved  = {cwb[-9]} {cwb1[-9]}
        Bit  9 :          Reserved  = {cwb[-10]} {cwb1[-10]}
        Bit 10 :        REMOTE_CMD  = {cwb[-11]} {cwb1[-11]}
        Bit 11 :      EXT_CTRL_LOC  = {cwb[-12]} {cwb1[-12]}
        Bit 12 :            USER_0  = {cwb[-13]} {cwb1[-13]}
        Bit 13 :            USER_1  = {cwb[-14]} {cwb1[-14]}
        Bit 14 :            USER_2  = {cwb[-15]} {cwb1[-15]}
        Bit 15 :            USER_3  = {cwb[-16]} {cwb1[-16]}
        '''
    print(control_word_description)


    
if __name__ == "__main__":
    # print(get_bit_from_list(bit_nums(), 15))

    # print(bit_nums()[-5])
    # print(int_to_bits(1142),"\n")
    # print(bit_nums())
    # print(int_to_bits(1150),"\n")
    # print(bit_nums())
    # print(int_to_bits(1151),"\n")
    # print(bytes_to_bits(0x32e2))
    # print(int_to_bits(0x0002))
    # print(int_to_bits(4736))
    # rsw(4736)
    print("int_to_bits(1143): ",int_to_bits(1143))
    print("bit_list_to_int(int_to_bits(1143)): ",bit_list_to_int(int_to_bits(1143)))
    
    # print(int_to_bits(1142))
    # print(hex(1142))

