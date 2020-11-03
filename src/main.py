import serial
from _curses import baudrate
import array as arr
import time
from functools import reduce
from libscrc import modbus
import json
import requests
import datetime
from centralnode import centralnode
from centralnode import loranode
send_pre = [5,0,1,14,0,2,0,7,1,8]
thing_speak ={    "write_api_key": "PYF7YMZNOM3TJVSM",
                        "updates": [{
                                    "created_at": "2020-10-30 13:38:2 -0400",
                                    "field1": 0,
                                    "field2": 0
                                    }
                                    ]    
            }
def save2file(file, data):
    file.seek(0)
    file.truncate()
    json.dump(data, file) 

def init_serial_port(Port):
    try:
        ser = serial.Serial(Port,timeout=0.6)
    except:
        print("Serial port does not exists")
        quit()
        return False
    print("Port ",ser.name," opened")
    ser.close
    print("port closed")
    return True
    
def get_modbus_pdu(id, slaves):
    if slaves==None:
            print("Empty")
            return
    else:
            adu = []
            adu.append(id) 
            adu.append(4)
            adu.append(0)
            adu.append(1)
            adu.append(0)  
            quantity =len(slaves)*2
            adu.append(quantity)
            crc=(modbus(bytearray(adu))).to_bytes(2,'big')
            adu.append(crc[1])
            adu.append(crc[0])
            return adu

def get_modbus_adu(id,code,start_add,quantity):
    if quantity>125:
        return   
    adu = []
    adu.append(id)
    adu.append(code)
    start = (start_add).to_bytes(2,'big')
    adu.append(start[0])
    adu.append(start[1])
    q = (quantity).to_bytes(2,'big')
    adu.append(q[0])
    adu.append(q[1])
    crc=(modbus(bytearray(adu))).to_bytes(2,'big')
    adu.append(crc[1])
    adu.append(crc[0])
    print("modbus adu to send: ",adu)
    return adu
    
       
def lora_send(frame):
    print("sending...")
    ser = serial.Serial(node.lora_port,timeout=14)
    ser.write(bytearray(frame))
    print("Sent")
    print("Waiting answer...")
    expected_size = 22+2*frame[15]
    input_data=ser.read(size=expected_size)
    print("Data received")
    print(len(input_data))
    return input_data
    
def parse_modbus(frame):
    crc_r=modbus(frame)
    data =[]
    if crc_r==0:
        print("modbus correct")
        print(frame)
        quantity = (len(frame)-5)//4
        print(quantity)
        for i in range(quantity):
            pulses= int(frame[3+i*4:7+i*4].hex(),16)
            print(pulses)
            data.append(pulses)
        print("data: ",data)
        return data                
        
def poll_loras(loras):
    print("star polling")
    for lora_dic in loras:
        lora = loranode(lora_dic)
        print(lora.slaves)
        n=lora.quantity_poll()
        for i in range(n):
            print("poll ",i)
            max=lora.maxpoll_size
            quant = max
            if i == n-1:
                quant = lora.lastpollsize
            payload=get_modbus_adu(lora.id,4,1+i*max,quant)
            print("result",node.send(payload))
            response= node.receive()
            if response == None:
                continue
            data=parse_modbus(response)
            
            lora_hex =(lora.id).to_bytes(2,"big")
            for j,_ in enumerate(data):
                index = i* max // 2 + j+1
                serial_meter = lora_hex+(index).to_bytes(1,'big')
                print("index: ",serial_meter)
                energy_dic[serial_meter.hex()]=data[i]
                save2file(energy_file,energy_dic)


def post(data):
    print("posting...")
    now=datetime.datetime.now()
    now =str(now)+" -0400"
    print(now)
    update_data=thing_speak['updates'][0]
    update_data['created_at']=now
    update_data['field1']=data['000201']
    update_data['field2']=data['000202']
    thing_speak['updates'][0]=update_data
    print(thing_speak)
    headers = {'Content-type': 'application/json'}
    r = requests.post('https://api.thingspeak.com/channels/1212777/bulk_update.json', json=thing_speak,headers=headers)
    print("Status code is :",r.status_code)
    
    
        
    
if __name__ == "__main__":
    print("App started")
    node = centralnode("config.json")
    
    energy_file=open(node.energy_path,'r+')
    energy_dic = json.load(energy_file)
    
    for lora in node.loras:
        for slave in lora['slaves']:
            id_meter=(lora['loraid']).to_bytes(2,'big')+(slave).to_bytes(1,'big')
            if id_meter.hex() not in energy_dic.keys():
                     energy_dic[id_meter.hex()]=0
        print("Energy updated ",energy_dic)
        save2file(energy_file,energy_dic)
                 
    init_serial_port(node.lora_port)
    
    energy_file.close()
    energy_file=open(node.energy_path,'r+')
    energy_dic=json.load(energy_file)
    poll_loras(node.loras)
    energy_file.close()
    print("App Finished")
    
    #counter=0
    #===========================================================================
    #while True:
    #    energy_file=open(node.energy_path,'r+')
    #    energy_dic=json.load(energy_file)
    #    poll_loras(nodos)
    #   energy_file.close()
    #    if counter==120:
    #        post(energy_dic)
    #        counter=0
    #    counter+=1
    #    print("Print in :", 120-counter, " s")
