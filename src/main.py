#! /bin/env python3
import os
import time
import sys
from centralnode import *
from cipher import *
from files_management import *
from modbus_process import *
from post_http import post_scada
import serial
from watchdog import Watchdog
from logger import build_logger
import argparse
import subprocess
import logging
from threading import Timer

send_pre = [5, 0, 1, 14, 0, 2, 0, 7, 1, 8]
 
def post_thread(): 
    global counter
    global post_time_s
    counter+=1
    log.info("Posting in %s s",str(post_time_s - counter + 1))
    if counter == post_time_s :
        post_scada(node.post_path,args.production)
        counter = 0
    post_timer = Timer(1.0,post_thread)
    post_timer.start()
    

def build_argparser():
    label = subprocess.check_output(["git", "describe"]).strip()
    parser = argparse.ArgumentParser(description="To select production code")
    parser.add_argument('-p','--production', action='store_true', default=False, help = "Create production code")
    parser.add_argument('-v','--version', action='version', version=label.decode("utf-8"))
    return parser


def init_serial_port(Port):
    try:
        ser = serial.Serial(Port, timeout=0.6)
    except serial.SerialException:
        log.error("Problems: %s %s ", "could not open port ", Port)
        os._exit(0)
    log.debug("Port  %s %s", ser.name, " Available")
    ser.close()


def poll_loras(loras):
    log.info("Start polling")
    for lora_dic in loras:
        time.sleep(5)
        lora = loranode(lora_dic)
        log.debug("slaves members: %s", str(lora.slaves))
        n = lora.quantity_poll()
        for i in range(n):
            log.info("Poll %s %s in LoRa %s", str(i + 1), "th", lora.id)
            max_num_reg = lora.maxpoll_size
            quant = max_num_reg
            if i == n - 1:
                quant = lora.lastpollsize
            if lora.slaves[0] == 0:
                payload = get_modbus_adu(lora.id, 4, lora.id, quant)
            else:
                payload = get_modbus_adu(lora.id, 4, 1 + i * max_num_reg,
                                         quant)
            dest_slave = payload[0]
            if node.cipher:
                payload = encrypt_md(payload, "CFB")
            result = node.send(payload, dest_slave, quant)
            log.debug("Result %s", str(list(result)))
            log.info("Result code from sent [%d] ", result[6])

            response = node.receive()
            if response is None:
                continue
            if node.cipher:
                response = decrypt_md(response, "CFB")
            data = parse_modbus(response)
            if data is None:
                continue
            lora_hex = (lora.id).to_bytes(2, "big")
            for j, _ in enumerate(data):
                index = lora.slaves[j]
                serial_meter = lora_hex + (index).to_bytes(1, 'big')

                update_energy_file(serial_meter, data[j])
                update_post_file(serial_meter, data[j])


if __name__ == "__main__":
    
    args = build_argparser().parse_args()
    log = build_logger()

    log.info("App started")
    wtd_start = Watchdog(20)
    node = centralnode("json/config.json")
    init_serial_port(node.lora_port)
    if not node.init_lora():
        log.error("Could not config LoRa")
        os._exit(0)
    try:
        f_energy_boot(node.loras, node.energy_path)
        f_post_boot(node.loras, node.post_path)
        counter = 0
        post_time_s = node.post_time
        post_timer = Timer(1.0,post_thread)
        post_timer.start()
        node.ser = serial.Serial(node.lora_port, timeout=14)
        wtd_start.stop()
    except Watchdog:
        log.error("Reseting script due to wdt boot")
    wtd = Watchdog(300) # 5min
    try:
        while True:
            poll_loras(node.loras)
            print(
                "__________________________________________________________________"
            )
            wtd.reset()
    except KeyboardInterrupt:
        log.error("App finished!")
        os._exit(0)
    except Watchdog:
        wtd_start.stop()
    except Exception:
        log.error("App Crashed!")
        log.error("Problems? %s", sys.exc_info())
        log.info("Restarting...")
        os.execv(sys.executable, ['python'] + sys.argv)        
