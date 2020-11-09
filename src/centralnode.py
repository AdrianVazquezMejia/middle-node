import json
from functools import reduce
import serial


class centralnode:

    def __init__(self, config_path):
        config_file = open(config_path, 'r')
        config_dic = json.load(config_file)
        
        self.id = config_dic['ID']
        self.lora_port = config_dic['Serial Port']
        self.energy_path = config_dic['energy_path']
        self.post_path = config_dic['post_path']
        self.loras = config_dic['loras']
        
        print("This node ID: ", config_dic['ID'])
        print("Lora Serial Port: ", config_dic['Serial Port'])
        print("Energy path: ", self.energy_path)
        
        self.lora_list = []
        
        for i in self.loras:
            # print(i)
            self.lora_list.append(i['loraid'])
        # print(self.lora_list)   
        config_file.close()
    
    def send(self, payload):
        print("Sending...")
        pre_frame = [5, 0, 1, 14, 0, 2, 0, 7, 1, 8]
        if payload[1] == 4:
            pre_frame[3] = 14
        pre_frame[5] = payload[0]
        frame = pre_frame + payload 
        check_sum = reduce(lambda x, y: x ^ y, frame) 
        frame.append(check_sum)
        self.ser = serial.Serial(self.lora_port, timeout=14)
        self.ser.write(bytearray(frame))
        print("Data sent")
        self.expected_size = 22 + 2 * frame[15]
        return None
    
    def receive(self):
        print("receiving...")
        response = self.ser.read(size=self.expected_size)
        print("received:", response)
        if len(response) == 0:
            return
        if len(response) == self.expected_size:
            return response[16:self.expected_size - 1]

        
class loranode:

    def __init__(self, dic):
        self.id = dic['loraid']
        self.slaves = dic['slaves']
        self.maxpoll_size = 56
        self.lastpollsize = len(self.slaves) * 2 % self.maxpoll_size
        
    def quantity_poll(self):
        n = len(self.slaves) * 2 // self.maxpoll_size
        if self.lastpollsize != 0:
            n += 1
        return n   
        
        
