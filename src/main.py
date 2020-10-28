import serial
from _curses import baudrate
import array as arr
import time
from functools import reduce
from libscrc import modbus
nodos=[[0],[1,2,3],[1 ,2]]
test_frame=b'\x05\x00\x01\x0e\x00\x02\x00\x07\x01\x08\xff\x04\x00\x01\x00\x04\xb5\xd7\x9a'
send_pre = [5,0,1,14,0,2,0,7,1,8]
def init_serial_port():
    try:
        ser = serial.Serial('/dev/ttyUSB2',timeout=3)
    except:
        print("Serial port does not exists")
        return
    print("Port ",ser.name," opened")
    ser.close
    print("port closed")
def get_modbus_pdu(id, slaves):
    if len(slaves)==1 and slaves[0]==0:
            print("Empty")
            return
    else:
            adu=[]
            adu.append(id) 
            adu.append(4)
            adu.append(0)
            adu.append(1)
            adu.append(0)  
            quantity =len(slaves)
            adu.append(quantity)
            crc=(modbus(bytearray(adu))).to_bytes(2,'big')
            adu.append(crc[1])
            adu.append(crc[0])
            return adu
def poll_loras():
    
    for lora_id,slaves in enumerate(nodos):
        modbus_pdu=get_modbus_pdu(lora_id, slaves)
        print(modbus_pdu)

if __name__ == "__main__":
    print("Hello World")
    init_serial_port()
    poll_loras()
    #print(send_pre)
    #res = reduce(lambda x, y: x ^ y, send_pre) 
    #crc =modbus(test_frame)
    #print((crc).to_bytes(2,"big"))
# printing result  
    #print("The Bitwise XOR of list elements are : " + str(res))
    
    
    
