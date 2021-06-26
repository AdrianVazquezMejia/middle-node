from libscrc import modbus
import logging

log = logging.getLogger('central')
ch = logging.NullHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
log.addHandler(ch)


def get_modbus_adu_update(id, function, address, value):
    adu = []
    adu.append(id)
    adu.append(5)  #Write single coil
    adu.append(0)
    if function == "Reset":
        adu.append(address)  #TODO reset another address
    else:
        adu.append(address)
    if value == True:
        adu.append(255)
    else:
        adu.append(0)
    adu.append(0)
    crc = (modbus(bytearray(adu))).to_bytes(2, 'big')
    adu.append(crc[1])
    adu.append(crc[0])
    log.debug("modbus adu to send: %s", str(adu))
    return adu


def get_modbus_adu(id_slave, function_code, start_add, quantity):
    if quantity > 125:
        return None
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
    log.debug("modbus adu to send: %s", str(adu))
    return adu


# Verifico el crc y creo una lista con los datos recibidos de salida
def parse_modbus(frame):
    crc_r = modbus(frame)
    data = []
    if crc_r == 0:
        log.info("modbus correct")
        log.debug(str(list(frame)))
        quantity = (len(frame) - 5) // 4
        log.debug(str(quantity))
        for i in range(quantity):
            pulses = int(frame[3 + i * 4:7 + i * 4].hex(), 16)
            data.append(pulses)
        log.debug("data: %s", str(data))
        return data
    log.error("CRC error")
    return None
