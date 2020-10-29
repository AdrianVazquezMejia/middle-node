import serial
from _curses import baudrate
import array as arr
import time
from functools import reduce
from libscrc import modbus
import json
send_pre = [5,0,1,14,0,2,0,7,1,8]

def init_serial_port(Port):
    try:
        ser = serial.Serial(Port,timeout=0.6)
    except:
        print("Serial port does not exists")
        quit()
        return
    print("Port ",ser.name," opened")
    ser.close
    print("port closed")
    
def get_modbus_pdu(id, slaves):
    if slaves==None:
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
        
def lora_send(frame):
    print("sending...")
    ser = serial.Serial(config_dic['Serial Port'],timeout=3)
    ser.write(bytearray(frame))
    print("Sent")
    print("Waiting answer...")
    expected_size = 22+2*frame[15]
    input_data=ser.read_until(size=expected_size)
    print("Data received")
    return input_data
    
    
def poll_loras(conf):
    
    for lora_id,slaves in enumerate(nodos):
        modbus_pdu=get_modbus_pdu(lora_id, slaves)
        if modbus_pdu!=None:
            send_pre[5]=lora_id          
            lora_pdu=send_pre+modbus_pdu
            check_sum=reduce(lambda x, y: x ^ y, lora_pdu) 
            lora_pdu.append(check_sum)
            print(lora_pdu)
            answer=lora_send(lora_pdu)
            print(list(answer))

if __name__ == "__main__":
    print("App started")
    config_file=open("config.json")
    config_dic=json.load(config_file)
    
    print("ID: ",config_dic['ID'])
    print("Serial Port: ",config_dic['Serial Port'])
    print(config_dic['nodos'])
    
    nodos=[]
    config_nodos= config_dic['nodos']
    for i in config_nodos:
        nodos.append(config_nodos[i])
        print(config_nodos[i])
    init_serial_port(config_dic['Serial Port'])
    poll_loras(nodos)
    
    print("spce")
    
    


    
    
