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
    ser = serial.Serial(config_dic['Serial Port'],timeout=14)
    ser.write(bytearray(frame))
    print("Sent")
    print("Waiting answer...")
    expected_size = 22+2*frame[15]
    input_data=ser.read_until(size=expected_size)
    print("Data received")
    return input_data
    
    
def poll_loras(nodos):
    
    for lora_id,slaves in enumerate(nodos):
        print("Polling Lora: ",lora_id)
        modbus_pdu=get_modbus_pdu(lora_id, slaves)
        if modbus_pdu!=None:
            send_pre[5]=lora_id          
            lora_pdu=send_pre+modbus_pdu
            check_sum=reduce(lambda x, y: x ^ y, lora_pdu) 
            lora_pdu.append(check_sum)
            #print(lora_pdu)
            answer=lora_send(lora_pdu)
            #print(list(answer))
            expected_size = 22+2*lora_pdu[15]
            if len(answer)==expected_size:
                modbus_r= answer[16:expected_size-1]
                print(list(modbus_r))
                crc_r=modbus(modbus_r)
                if crc_r==0:
                    print("modbus correct")


    
if __name__ == "__main__":
    print("App started")
    config_file=open("config.json",'r')
    config_dic=json.load(config_file)
    energy_file=open('../output/energy.json','r+')
    energy = json.load(energy_file)
    
    print("ID: ",config_dic['ID'])
    print("Serial Port: ",config_dic['Serial Port'])
    print(config_dic['nodos'])
    
    nodos=[]
    
    node_id= int(config_dic['ID'],16)
    
    # Manage the json to stores the energy
    config_nodos= config_dic['nodos']
    for index,i in enumerate(config_nodos):
        nodos.append(config_nodos[i])
        if config_nodos[i]!=None:
            for j in config_nodos[i]:
                id_hex=(index).to_bytes(2,'big')
                serial_nodo=id_hex+(j).to_bytes(1,'big')
                if serial_nodo.hex() not in energy.keys():
                    energy[serial_nodo.hex()]=0
            print("Energy ",energy)
            energy_file.seek(0)
            energy_file.truncate()
            json.dump(energy, energy_file)
            energy_file.close()
    
       
        
        
        
    
    init_serial_port(config_dic['Serial Port'])
    #while True:
    #    poll_loras(nodos)
    id_hex=(12).to_bytes(2,'big')
    s=id_hex+b'\x01'
    print(s)
    print(s.hex())
    


    
    
