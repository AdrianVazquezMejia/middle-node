from functools import reduce
import json
import sys
import os
import serial
import logging
from Crypto.Util.number import size


log = logging.getLogger('central')
ch = logging.NullHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
log.addHandler(ch)

class ConfigError(Exception):
    """! Set error message

    """
    def __init__(self):
        self.message = "Can not config"


# Esta clase contiene la informacion del nodo
class centralnode:
    """! Organize node's information

    """
    def __init__(self, config_path):
        """! Set node's characteristics

        @param config_path       file to keep the information
        """
        config_file = open(config_path, 'r')
        config_dic = json.load(config_file)
        config_file.close()

        self.id = config_dic['ID']
        self.key = config_dic["write_api_key"]
        self.lora_port = config_dic['Serial Port']
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
        log.info("This node ID: %s ", str(config_dic['ID']))
        log.debug("Lora Serial Port: %s ", str(config_dic['Serial Port']))
        self.lora_list = []

        for i in self.loras:
            self.lora_list.append(i['loraid'])

    @staticmethod
    def build_send_frame(payload, dest_slave):
        """! Organize data in a dictionary to send

        @param payload       charge of the meter
        @param dest_slave    slave of destination

        @return frame        dictionary with meters' information
        """
        log.debug("Sending...")
        pre_frame = [5, 0, 1, 14, 0, 2, 0, 7, 1, 8]
        if payload[1] == 4:
            pre_frame[3] = 14
        pre_frame[5] = dest_slave
        frame = pre_frame + payload
        check_sum = reduce(lambda x, y: x ^ y, frame)
        frame.append(check_sum)
        return frame

    def send(self, payload, dest_slave, quant = 0):
        """! Send received information of the pool 

        @param payload       charge of the meter
        @param dest_slave    slave of destination
        @param quant         maximum size of the poll

        @return result       information of the data
        """   
        frame = self.build_send_frame(payload, dest_slave)
        #self.ser = serial.Serial(self.lora_port, timeout=14)
        self.ser.write(bytearray(frame))
        result = self.ser.read(size = 8)
        log.debug("Data sent : %s", str(frame))
        self.expected_size = 22 + 2 * quant -8
        if quant == 0 :
            self.expected_size = 17

        return result

    def receive(self):
        """! Send a message of received or
        an error message if there is any mistake

        @return response         data frame  
        """
        log.debug("receiving...")
        response = self.ser.read(size=self.expected_size)
        log.debug("received: %s", str(list(response)))
        if len(response) == self.expected_size:
            return response[8:self.expected_size - 1]
        log.error("Unexpected data lenght received %s", str(list(response)))
        return None

    def config_trama(self):
        """! Organize the order of the data frame

        @return config_frame    organized data to send
        """
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
        """! Initialize Lora with the respective characteristics

        @return True or False value of the Lora configuration
        """
        expect = [
            1, 0, 129, 12, 165, 165, 108, 64, 18, 7, 0, 0, 1, 1, 0, 3, 0]
        try:
            expect[12] = self.networkid
            check_sum = reduce(lambda x, y: x ^ y, expect)
            expect.append(check_sum)
            config_frame = self.config_trama()
            self.ser = serial.Serial(self.lora_port, timeout=5)
            self.ser.write(bytearray(config_frame))
            log.debug("Config frame: %s", str(config_frame))
            response = self.ser.read(size=18)
            log.debug("Config Response: %s", str(list(response)))
            version = self.ser.read(size=34)
            log.info("Version LoRa: %s", version)
        except Exception:
            log.error("Serial Port problem")
            log.error("Problems? %s", sys.exc_info())
            os._exit(0)
        if list(response) != expect:
            expect[3] = 13
            expect[17] = expect[17]+1
            if list(response) == expect:
                    self.ser.close()
                    log.info("Lora Config Successfull")
                    return True
            return False
        self.ser.close()
        log.info("Lora Config Successfull")
        return True


class loranode:
    """ Determine the quantity of Loras 

    """
    def __init__(self, dic):
        """! Set meter and poll characteristics

        @param dic             dictionary of meter's information
        """
        self.id = dic['loraid']
        self.slaves = dic['slaves']
        self.maxpoll_size = 56
        self.lastpollsize = len(self.slaves) * 2 % self.maxpoll_size

    def quantity_poll(self):
        """! Set the quantity of pools

        """
        n = len(self.slaves) * 2 // self.maxpoll_size
        if self.lastpollsize != 0:
            n += 1
        return n

    