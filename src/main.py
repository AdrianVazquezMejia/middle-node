#! /bin/env python3
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
from watchdog import Watchdog
from cipher import encrypt_md
send_pre = [5, 0, 1, 14, 0, 2, 0, 7, 1, 8]
thing_speak = {    "write_api_key": "PYF7YMZNOM3TJVSM",
                        "updates": [{
                                    "created_at": "2020-10-30 13:38:2 -0400",
                                    "field1": 0,
                                    "field2": 0
                                    }
                                    ]    
            }

# Actualizo los archivos
def save2file(file, data):
    file.seek(0)
    file.truncate()
    json.dump(data, file) 

# Pruebo el puerto serial
def init_serial_port(Port):
    try:
        ser = serial.Serial(Port, timeout=0.6)
    except:
        print("Serial port does not exists")
        quit()
        return False
    print("Port ", ser.name, " opened")
    ser.close
    print("port closed")
    return True
    
# Creo una adu modbus segun los datos de entrada
def get_modbus_adu(id, function_code, start_add, quantity):
    if quantity > 125:
        return   
    adu = []
    adu.append(id)
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
        for i in range(quantity):
            pulses = int(frame[3 + i * 4:7 + i * 4].hex(), 16)
            data.append(pulses)
        print("data: ", data)
        return data
    else:
        print("CRC error")
        return                

     
def poll_loras(loras):
    print("Start polling")
    for lora_dic in loras:          #Itero en torno a cada LoRa
        lora = loranode(lora_dic)   # Creo un objeto con el dicionario
        print("slaves members: ",lora.slaves)
        n = lora.quantity_poll()    # obtengo el numero de interrogaciones por lora
        for i in range(n):          # Itero en torno a ese numero
            print("Poll ", i + 1, "th")
            max = lora.maxpoll_size # Maximo numero de registros por interrogacion
            quant = max
            if i == n - 1:
                quant = lora.lastpollsize       # Cantidad de registros del ultimo poll 
            if lora.slaves[0]==0:
                payload = get_modbus_adu(lora.id, 4, lora.id, quant)
            else:
                payload = get_modbus_adu(lora.id, 4, 1 + i * max, quant)    # Obtengo la trama modbus
            if node.cipher:
               encrypt_md(payload,"CFB")
            print("result", node.send(payload))   # Envio los datos
            response = node.receive()               # Espero la respuesta
            if response == None:
                continue
            data = parse_modbus(response)           # Si es valida verifico los datos
            
            if data == None:
                continue
            lora_hex = (lora.id).to_bytes(2, "big")     # Una rutina para actulizar los archivos
            for j, _ in enumerate(data):
                index = lora.slaves[j] #i * max // 2 + j + 1
                print("INDEX: ", j)
                serial_meter = lora_hex + (index).to_bytes(1, 'big')
                energy_dic[serial_meter.hex()] = data[i]
                save2file(energy_file, energy_dic)
                
                for meter_dic in updates:
                    if serial_meter.hex() == meter_dic['meterid']:                
                        meter_dic["energy"] = data[i]
                        now = datetime.datetime.now()
                        now = str(now) + " -0400"
                        meter_dic["date"] = now
                        print("updated  ", meter_dic)
                        break 
                    
                post_dic['updates'] = updates
                save2file(post_file, post_dic)

 
def post_thingS(data):
    print("posting...")
    now = datetime.datetime.now()
    now = str(now) + " -0400"
    print(now)
    update_data = thing_speak['updates'][0]
    update_data['created_at'] = now
    update_data['field1'] = data['000201']
    update_data['field2'] = data['000202']
    thing_speak['updates'][0] = update_data
    print(thing_speak)
    headers = {'Content-type': 'application/json'}
    r = requests.post('https://api.thingspeak.com/channels/1212777/bulk_update.json', json=thing_speak, headers=headers)
    print("Status code is :", r.status_code)        

    
def post_scada(data_dic):
    print("Posting to Scada")
    print("Data to post: ", data_dic)
    headers = {'Content-type': 'application/json'}
    r = requests.post('https://glacial-beach-93230.herokuapp.com/api/data', json=data_dic, headers=headers)
    print("Status code is :", r.status_code)
    print(r)
    
     
if __name__ == "__main__":
    print("App started")
    # Create wdt
    
    wtd_start = Watchdog(20)
    try:
 
        # class central node posee los datos del nodo.
        # Nodo es este raspberry
        node = centralnode("../json/config.json")
        node.init_lora()
        # Abrir el archivo de  que guarda solo la energia
        energy_file = open(node.energy_path, 'r+')
        energy_dic = json.load(energy_file)
        
        # Abrir el archivo que guarda los datos a publicar 
        post_file = open(node.post_path, 'r+')
        post_dic = json.load(post_file)
        print("post dic", post_dic)
        updates = post_dic['updates']
        print(updates)
        
        # Actualiza el archivo de energia por si se agregaron medidores
        for lora in node.loras:
            for slave in lora['slaves']:
                id_meter = (lora['loraid']).to_bytes(2, 'big') + (slave).to_bytes(1, 'big')  #
                if id_meter.hex() not in energy_dic.keys():
                         energy_dic[id_meter.hex()] = 0
            print("Energy updated ", energy_dic)
            save2file(energy_file, energy_dic)
        energy_file.close()            
        
        #actualiza el archivo para publicar
        for lora in node.loras:
            for slave in lora['slaves']:
                id_meter = (lora['loraid']).to_bytes(2, 'big') + (slave).to_bytes(1, 'big')
                print("idmeter: ", id_meter.hex())
                isUpdate = False
                for i in updates:
                    isUpdate = False
                    if id_meter.hex() == i['meterid']:
                        isUpdate = True
                        break
                if not isUpdate:
                    meter_dic = {}
                    meter_dic["meterid"] = id_meter.hex()
                    meter_dic["energy"] = 0
                    now = datetime.datetime.now()
                    now = str(now) + " -0400"
                    meter_dic["date"] = now
                    updates.append(meter_dic)
                    print("appending ", updates) 
        post_dic['updates'] = updates
        save2file(post_file, post_dic)
        post_file.close()
        
        # Prueba el puerto serial
        init_serial_port(node.lora_port)
        
        energy_file = open(node.energy_path, 'r+')
        energy_dic = json.load(energy_file)
        poll_loras(node.loras)
        
        counter = 0
        # Tiempo de publicacion cada 2 min
        post_time_s = 100        
        # Cliclo para interrogar los LoRa
        wtd_start.stop()
    except Watchdog:
        print("Reseting script due to crashed")
  # handle watchdog error
    wtd = Watchdog(30)
    try:   
        while True:
            
            # Abro los archivos
            energy_file = open(node.energy_path, 'r+')
            energy_dic = json.load(energy_file)
            
            post_file = open(node.post_path, 'r+')
            post_dic = json.load(post_file)
            
            poll_loras(node.loras)   # Interrogo todos los LoRa
            
            energy_file.close()     # Cierro los archivos
            post_file.close()
            
            # Publico si llego a los 2 min
            if counter == post_time_s:
                post_thingS(energy_dic)
                post_scada(post_dic)
                counter = 0
            counter += 1
            print("Print in :", post_time_s - counter, " s")
            print("______________________________________")
            time.sleep(1)
            wtd.reset()
    except Watchdog:
        wtd_start.stop()
        
    print("App Finished")
