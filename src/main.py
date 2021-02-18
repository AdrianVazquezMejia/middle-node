#! /bin/env python3
import datetime
import json
import os
import sys
import time

from libscrc import modbus
import serial

from centralnode import centralnode
from centralnode import loranode
from cipher import decrypt_md
from cipher import encrypt_md
from post_http import post_scada
from watchdog import Watchdog
from files_management import f_energy_boot
from files_management import f_post_boot
send_pre = [5, 0, 1, 14, 0, 2, 0, 7, 1, 8]


# Actualizo los archivos
def save2file(file, data):
    file.seek(0)
    file.truncate()
    json.dump(data, file)


# Pruebo el puerto serial
def init_serial_port(Port):
    try:
        ser = serial.Serial(Port, timeout=0.6)
    except Exception:
        print("Problems?", sys.exc_info())
        print("Serial port does not exists")
        sys.exit()
        return False
    print("Port ", ser.name, " opened")
    ser.close()
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
    print("CRC error")
    return


def poll_loras(loras):
    print("Start polling")
    for lora_dic in loras:  # Itero en torno a cada LoRa
        time.sleep(1)
        lora = loranode(lora_dic)  # Creo un objeto con el dicionario
        print("slaves members: ", lora.slaves)
        n = lora.quantity_poll(
        )  # obtengo el numero de interrogaciones por lora
        for i in range(n):  # Itero en torno a ese numero
            print("Poll ", i + 1, "th")
            max_num_reg = lora.maxpoll_size  # Maximo numero de registros por interrogacion
            quant = max_num_reg
            if i == n - 1:
                quant = lora.lastpollsize  # Cantidad de registros del ultimo poll
            if lora.slaves[0] == 0:
                payload = get_modbus_adu(lora.id, 4, lora.id, quant)
            else:
                payload = get_modbus_adu(lora.id, 4, 1 + i * max_num_reg,
                                         quant)  # Obtengo la trama modbus
            dest_slave = payload[0]
            if node.cipher:
                payload = encrypt_md(payload, "CFB")
            node.send(payload, dest_slave, quant)  # Envio los datos
            response = node.receive()  # Espero la respuesta
            if response is None:
                continue
            if node.cipher:
                response = decrypt_md(response, "CFB")
            data = parse_modbus(response)  # Si es valida verifico los datos
            if data is None:
                continue
            lora_hex = (lora.id).to_bytes(
                2, "big")  # Una rutina para actulizar los archivos
            for j, _ in enumerate(data):
                index = lora.slaves[j]  # i * max_num_reg // 2 + j + 1
                serial_meter = lora_hex + (index).to_bytes(1, 'big')
                energy_dic[serial_meter.hex()] = data[j]
                save2file(energy_file, energy_dic)
                updates = post_dic['updates']
                for meter_dict in updates:
                    if serial_meter.hex() == meter_dict['meterid']:
                        meter_dict["energy"] = data[j]
                        now = datetime.datetime.now()
                        now = str(now) + " -0400"
                        meter_dict["date"] = now
                        print("updated  ", meter_dict)
                        break

                post_dic['updates'] = updates
                save2file(post_file, post_dic)


if __name__ == "__main__":
    print("App started")
    # Create wdt

    wtd_start = Watchdog(20)
    node = centralnode("json/config.json")
    if not node.init_lora():
        os._exit(0)
    try:

        # class central node posee los datos del nodo.
        # Nodo es este raspberry

        # Actualiza el archivo de energia por si se agregaron medidores
        f_energy_boot(node.loras,node.energy_path)
        
        # actualiza el archivo para publicar
        f_post_boot(node.loras,node.post_path)
        
        # Prueba el puerto serial
        init_serial_port(node.lora_port)

        energy_file = open(node.energy_path, 'r+')
        energy_dic = json.load(energy_file)
        poll_loras(node.loras)

        counter = 0
        # Tiempo de publicacion cada 2 min
        post_time_s = 5
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

            poll_loras(node.loras)  # Interrogo todos los LoRa

            energy_file.close()  # Cierro los archivos
            post_file.close()

            # Publico si llego a los 2 min
            if counter == post_time_s:
                post_scada(post_dic)
                counter = 0
            counter += 1
            print("Print in :", post_time_s - counter, " s")
            print("____________________________________________________________________________")
            time.sleep(1)
            wtd.reset()
    except Watchdog:
        wtd_start.stop()

    print("App Finished")
