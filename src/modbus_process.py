from libscrc import modbus

def get_modbus_adu(id_slave, function_code, start_add, quantity):
    if quantity > 125:
        return
    adu = []
    adu.append(id_slave)
    adu.append(function_code)
    start = (start_add).to_bytes(2, 'big')
    adu.append(start[0])
    adu.append(start[1])
    q = (quantity).to_bytes(2, 'big')
    adu.append(q[0])
    adu.append(q[1])
    crc = (modbus(bytearray(adu))).to_bytes(2, 'big')
    adu.append(crc[1])
    adu.append(crc[0])
    print("modbus adu to send: ", adu)
    return adu


# Verifico el crc y creo una lista con los datos recibidos de salida
def parse_modbus(frame):
    crc_r = modbus(frame)
    data = []
    if crc_r == 0:
        print("modbus correct")
        print(list(frame))
        quantity = (len(frame) - 5) // 4
        print(quantity)
        for i in range(quantity):
            pulses = int(frame[3 + i * 4:7 + i * 4].hex(), 16)
            data.append(pulses)
        print("data: ", data)
        return data
    print("CRC error")
    return
