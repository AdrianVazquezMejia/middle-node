import datetime
import json
import logging
from pip.utils.outdated import SELFCHECK_DATE_FMT


log = logging.getLogger('files')
ch = logging.NullHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
log.addHandler(ch)

class MeterUpdate(object):
    def __init__(self, object_dic):
        self.lora_id =int(object_dic["meterid"][0:4],16)
        self.address = int(object_dic["meterid"][4:6],16)
        if self.address==0:
            self.address = self.lora_id
        if object_dic["isPowered"]:
            self.function = "Relay"
            self.value = object_dic["powerValue"]
        else:
            self.function = "Reset"
            self.value = True        
    

def save2file(file, data):
    file.seek(0)
    file.truncate()
    json.dump(data, file)


def update_post_file(serial, data):
    with open("json/post.json", 'r+') as post_file:
        post_dic = json.load(post_file)
        updates = post_dic['updates']
        for meter_dict in updates:
            if serial.hex() == meter_dict['meterid']:
                meter_dict["energy"] = data
                now = str(datetime.datetime.now())
                meter_dict["date"] = now
                log.debug("updated  %s", str(meter_dict))
                break
        post_dic['updates'] = updates
        save2file(post_file, post_dic)


def update_energy_file(serial, data):
    with open("output/energy.json", 'r+') as energy_file:
        energy_dic = json.load(energy_file)
        energy_dic[serial.hex()] = data
        log.info("Updated %s: %s at %s", serial.hex(), str(data),str(datetime.datetime.now()) )
        save2file(energy_file, energy_dic)


def f_energy_boot(loras, energy_path):
    energy_file = open(energy_path, 'r+')
    energy_dic = json.load(energy_file)
    for lora_edges in loras:
        for slave in lora_edges['slaves']:
            id_meter = (lora_edges['loraid']).to_bytes(
                2, 'big') + (slave).to_bytes(1, 'big')
            if id_meter.hex() not in energy_dic.keys():
                energy_dic[id_meter.hex()] = 0
        log.debug("Energy updated %s", str(energy_dic))
        save2file(energy_file, energy_dic)
    energy_file.close()


def f_post_boot(loras, post_path):
    post_file = open(post_path, 'r+')
    post_dic = json.load(post_file)
    log.debug("post dic %s", str(post_dic))
    updates = post_dic['updates']
    log.debug(str(updates))
    for lora_edges in loras:
        for slave in lora_edges['slaves']:
            id_meter = (lora_edges['loraid']).to_bytes(
                2, 'big') + (slave).to_bytes(1, 'big')
            log.debug("idmeter: %s", str(id_meter.hex()))
            isUpdate = False
            for update in updates:
                isUpdate = False
                if id_meter.hex() == update['meterid']:
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
                log.debug("appending %s", str(updates))
    post_dic['updates'] = updates
    save2file(post_file, post_dic)
    post_file.close()
        
       
def get_meter_updates():
    #get json from cloud
    with open("json/states.json") as status_file:
        status_dic = json.load(status_file)
        updates = status_dic["updates"]
        updates_list = []
        #log.debug(status_dic)s
        log.debug(updates)
        for update in updates:
            meter_update_object = MeterUpdate(update)
            log.debug(meter_update_object.lora_id)
            log.debug(meter_update_object.address)
            log.debug(meter_update_object.function)
            log.debug(meter_update_object.value)
            updates_list.append(meter_update_object)
            #payload = get_modbus_adu_update(meter_update_object.lora_id, meter_update_object.function,meter_update_object.address,meter_update_object.value)
            #log.debug(updates_list)
        return updates_list
        
if __name__ == "__main__":
     meter_updates =get_meter_updates()
     for update in meter_updates:
         print(update.lora_id)
    
