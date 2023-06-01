def clamp(le_data_b): # le_data_b in little endian order
    a_b = bytearray(le_data_b)
    a_b[0] &= 248  # 0.  byte: set the three least significant bits to 0
    a_b[31] &= 127 # 31. byte: set the most significant bit to 0
    a_b[31] |= 64  #           ...and the second-most significant bit to 1
    return bytes(a_b) 

# local helper for display
def display_bits(le_data_b):
    return bin(int.from_bytes(le_data_b, "big"))[2:].rjust(256, "0")
def display_bytes(le_data_b):
    return le_data_b.hex()
#
# test
#

le_data_b = bytes.fromhex("ee86be919516d75d619461f46b850ac641761373835019b5dccf82d8e2ca908f")
print("data, le, binary:          " + display_bits(le_data_b))
print("data, le, clamped, binary: " + display_bits(clamp(le_data_b)))
print("data, le, hex:             " + display_bytes(le_data_b))
print("data, le, clamped, hex:    " + display_bytes(clamp(le_data_b)))