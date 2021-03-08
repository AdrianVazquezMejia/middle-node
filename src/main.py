#! /bin/env python3
import os
import time

from centralnode import *
from cipher import *
from files_management import *
from modbus_process import *
from post_http import post_scada
import serial
from watchdog import Watchdog
import argparse
import subprocess

send_pre = [5, 0, 1, 14, 0, 2, 0, 7, 1, 8]


def build_argparser():
    label = subprocess.check_output(["git", "describe"]).strip()
    parser = argparse.ArgumentParser(description="To select production code")
    parser.add_argument('-p',
                        '--production',
                        action='store_true',
                        default=False,
                        help="Create production code")
    parser.add_argument('-v',
                        '--version',
                        action='version',
                        version=label.decode("utf-8"))
    return parser


def init_serial_port(Port):
    try:
        ser = serial.Serial(Port, timeout=0.6)
    except serial.SerialException:
        print("Problems: ", "could not open port ", Port)
        os._exit(0)
    print("Port ", ser.name, " Available")
    ser.close()


def poll_loras(loras):
    print("Start polling")
    for lora_dic in loras:
        time.sleep(1)
        lora = loranode(lora_dic)
        print("slaves members: ", lora.slaves)
        n = lora.quantity_poll()
        for i in range(n):
            print("Poll ", i + 1, "th")
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
            node.send(payload, dest_slave, quant)
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
    print("App started")
    wtd_start = Watchdog(20)
    node = centralnode("json/config.json")
    init_serial_port(node.lora_port)
    if not node.init_lora():
        print("Could not config LoRa")
        os._exit(0)
    try:
        f_energy_boot(node.loras, node.energy_path)
        f_post_boot(node.loras, node.post_path)
        wtd_start.stop()
    except Watchdog:
        print("Reseting script due to crashed")
    wtd = Watchdog(30)
    try:
        counter = 0
        post_time_s = node.post_time // len(node.loras)
        while True:
            poll_loras(node.loras)
            if counter == post_time_s:
                post_scada(node.post_path, args.production)
                counter = 0
            counter += 1
            print("Printing in :", post_time_s - counter, " s")
            print(
                "__________________________________________________________________"
            )
            wtd.reset()
    except KeyboardInterrupt:
        print("App finished!")
        os._exit(0)
    except Watchdog:
        wtd_start.stop()
