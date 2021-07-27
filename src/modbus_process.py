from libscrc import modbus
import logging
from functools import reduce

log = logging.getLogger('central')
ch = logging.NullHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
log.addHandler(ch)

def get_modbus_adu_update(id,function,address, value):
    """! Organize and update the data unity 
        of the application and send it

    @param id           ID of the unity
    @param function     the function of the application 
    @param address      station address 
    @param value        value of the received data

    @return adu         list of data unity of application 
    """
    adu = []
    adu.append(id)
    adu.append(5) #Write single coil
    adu.append(0)
    if function == "Reset":
        adu.append(address) #TODO reset another address
    else:
        adu.append(address)
    if value == True:
        adu.append(255)
    else:
        adu.append(0)
    hash = reduce(lambda x, y: x ^ y, adu)
    adu.append(hash)
    crc = (modbus(bytearray(adu))).to_bytes(2, 'big')
    adu.append(crc[1])
    adu.append(crc[0])

    log.debug("hash to write: %s", str(hash))
    log.debug("modbus adu to send: %s", str(adu))
    return adu

def get_modbus_adu(id_slave, function_code, start_add, quantity):
    """! Organize the data in a list and return it

    @param id_slave           ID of the unity's slave     
    @param function_code      function application code
    @param start_add          initial value to add
    @param quantity           quantity of data

    @return adu               list of data unity of application
    """    
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
    """! Verify errors in the data unity and send the 
    received data

    @param frame       data frame received                    

    @return data       list of data frame received             
    """
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
