from functools import reduce
import json
import sys
import unittest

import serial


class ConfigError(Exception):
    def __init__(self):
        self.message = "Can not config"


# Esta clase contiene la informacion del nodo
class centralnode:
    def __init__(self, config_path):
        config_file = open(config_path, 'r')
        config_dic = json.load(config_file)
        config_file.close()

        self.id = config_dic['ID']
        self.lora_port = config_dic['Serial Port']
        self.energy_path = config_dic['energy_path']
        self.post_path = config_dic['post_path']
        self.loras = config_dic['loras']
        self.networkid = config_dic['Networkid']
        self.baudarate = config_dic['Baudarate']
        self.post_time = config_dic['post_time']
        self.ser = None
        self.expected_size = None
        if config_dic["Cipher payload"] == "true":
            self.cipher = True
        else:
            self.cipher = False
        print("This node ID: ", config_dic['ID'])
        print("Lora Serial Port: ", config_dic['Serial Port'])
        print("Energy path: ", self.energy_path)

        self.lora_list = []

        for i in self.loras:
            self.lora_list.append(i['loraid'])

    def build_send_frame(self, payload, dest_slave):
        print("Sending...")
        pre_frame = [5, 0, 1, 14, 0, 2, 0, 7, 1, 8]
        if payload[1] == 4:
            pre_frame[3] = 14
        pre_frame[5] = dest_slave
        frame = pre_frame + payload
        check_sum = reduce(lambda x, y: x ^ y, frame)
        frame.append(check_sum)
        return frame

    def send(self, payload, dest_slave, quant):
        frame = self.build_send_frame(payload, dest_slave)
        self.ser = serial.Serial(self.lora_port, timeout=14)
        self.ser.write(bytearray(frame))
        print("Data sent :", frame)
        self.expected_size = 22 + 2 * quant

    def receive(self):
        print("receiving...")
        response = self.ser.read(size=self.expected_size)
        print("received:", list(response))
        if len(response) == 0:
            return
        if len(response) == self.expected_size:
            return response[16:self.expected_size - 1]

    def config_trama(self):
        lora_id = 256  # default
        fixed_frame = [1, 0, 1, 13, 165, 165, 108, 64, 18, 7, 0]
        bauda_hex = (self.networkid).to_bytes(2, 'big')
        config_frame = fixed_frame + list(bauda_hex)
        lora = (lora_id).to_bytes(2, 'big')
        config_frame = config_frame + list(lora)
        config_frame.append(3)  # 9600 baudios
        config_frame.append(0)
        check_sum = reduce(lambda x, y: x ^ y, config_frame)
        config_frame.append(check_sum)
        return config_frame

    def init_lora(self):
        expected_response = [
            1, 0, 129, 12, 165, 165, 108, 64, 18, 7, 0, 0, 1, 1, 0, 3, 0, 182
        ]
        config_frame = self.config_trama()
        self.ser = serial.Serial(self.lora_port, timeout=5)
        self.ser.write(bytearray(config_frame))
        print("Config frame: ", config_frame)
        response = self.ser.read(size=18)
        print("Config Response:", list(response))
        version = self.ser.read(size=34)
        print("Version LoRa:", version)
        if list(response) != expected_response:
            expected_response[3] = 13
            if list(response) == expected_response:
                return True
            return False
        self.ser.close()
        print("Lora Config Successfull")
        return True


class loranode:
    def __init__(self, dic):
        self.id = dic['loraid']
        self.slaves = dic['slaves']
        self.maxpoll_size = 56  # Para el tamano del payload es la maxima de cantidad de registros
        self.lastpollsize = len(self.slaves) * 2 % self.maxpoll_size

    def quantity_poll(self):
        n = len(self.slaves) * 2 // self.maxpoll_size
        if self.lastpollsize != 0:
            n += 1
        return n
