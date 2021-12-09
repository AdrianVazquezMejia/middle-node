#! /bin/env python3
import os
import time
import sys
from centralnode import *
from cipher import *
from modbus_process import *
from post_http import *
import serial
from watchdog import Watchdog
from logger import build_logger
import argparse
import subprocess
import logging
from threading import Timer
from sqlite_manager import *
from gpiozero import LED
from post_http import get_token

restart_button = LED(23)

send_pre = [5, 0, 1, 14, 0, 2, 0, 7, 1, 8]
MAX_ALL_FAIL_TOLERANCE = 5
RESTART_TIME = 3600


def refresh_token():
    global token
    log.info("Getting a brand new token")
    token_timer = Timer(24 * 3600, refresh_token)
    token_timer.start()
    token = get_token()


def restart_lora():
    log.info("Restart LoRa module")
    if args.production:
        restart_button.off()
        time.sleep(1)
        restart_button.on()
        time.sleep(5)


def restart_script():
    os.execv(sys.executable, ['python'] + sys.argv)


def post_thread():
    """! Post meters information
   
    """
    global counter
    global post_time_s
    global counter_restart
    counter += 1
    counter_restart += 1
    log.info("Posting in %s s", str(post_time_s - counter + 1))
    if counter == post_time_s:
        post_json = load_json(node.id, node.key)
        post_scada(post_json, args.production, token)
        counter = 0
    if counter_restart == RESTART_TIME:
        restart_script()

    post_timer = Timer(1.0, post_thread)
    post_timer.start()


def build_argparser():
    """! Set command line interface

    @return parser       usages messages  
    """
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
    """! Initialize serial port
   
    """
    try:
        ser = serial.Serial(Port, timeout=0.6)
    except serial.SerialException:
        log.error("Problems: %s %s ", "could not open port ", Port)
        os._exit(0)
    log.debug("Port  %s %s", ser.name, " Available")
    ser.close()


def poll_loras(loras):
    """! Search and set meters characteristics
    and then update them in the database
   
    """
    log.info("Start polling")
    lora_index = 0
    fail_array = [False] * len(loras)
    for lora_dic in loras:
        time.sleep(1)
        lora = loranode(lora_dic)
        log.debug("slaves members: %s", str(lora.slaves))
        n = lora.quantity_poll()
        global all_failed_counter
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
            if len(result) < 7:
                log.error("Inconsistent frame from LoRa")
                continue
            log.info("Result code from sent [%d] ", result[6])

            response = node.receive()
            if response is None:
                fail_array[lora_index] = True
                continue
            if node.cipher:
                response = decrypt_md(response, "CFB")
            data = parse_modbus(response)
            log.info("data from node %s ", str(data))
            if data is None:
                continue
            lora_hex = (lora.id).to_bytes(2, "big")
            for j, _ in enumerate(data):
                index = lora.slaves[j]
                serial_meter = lora_hex + (index).to_bytes(1, 'big')
                update_date_base(serial_meter.hex(), data[j])
        lora_index += 1
    if False not in fail_array:
        log.error("All nodes not responding!")
        all_failed_counter += 1

    if all_failed_counter == MAX_ALL_FAIL_TOLERANCE:
        log.debug("Maximum Fail Tolerance Reached")
        restart_script()

    time.sleep(5)
    meter_updates = get_meter_updates(token)
    for update in meter_updates:
        time.sleep(3)

        payload = get_modbus_adu_update(update.lora_id, update.function,
                                        update.address, update.value)
        unencripted_payload = payload
        log.debug(payload)
        dest_slave = payload[0]
        if node.cipher:
            payload = encrypt_md(payload, "CFB")
        result = node.send(payload, dest_slave)
        log.debug("Result %s", str(list(result)))
        log.info("Result code from sent [%d] ", result[6])

        response = node.receive()
        if response is None:
            continue
        if node.cipher:
            response = decrypt_md(response, "CFB")

        log.debug("message received: %s", str(unencripted_payload))

        if set(unencripted_payload) == set(response):
            log.info("Wrote Coils Successfully")
        else:
            log.info("Something went wrong writing coils")


if __name__ == "__main__":
    """! Main program entry
    
    """
    args = build_argparser().parse_args()
    log = build_logger()

    log.info("App started")
    wtd_start = Watchdog(20)
    node = centralnode("json/config.json")
    init_serial_port(node.lora_port)
    restart_lora()
    all_failed_counter = 0

    if not node.init_lora():
        log.error("Could not config LoRa")
        os._exit(0)
    try:
        energy_load(node.loras)
        counter = 0
        counter_restart = 0
        post_time_s = node.post_time
        post_timer = Timer(1.0, post_thread)
        post_timer.start()

        token = ''
        token_timer = Timer(1.0, refresh_token)
        token_timer.start()

        node.ser = serial.Serial(node.lora_port, timeout=14)
        wtd_start.stop()
    except Watchdog:
        log.error("Reseting script due to wdt boot")
    wtd = Watchdog(300)  # 5min
    try:
        while True:
            poll_loras(node.loras)
            log.info(
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
