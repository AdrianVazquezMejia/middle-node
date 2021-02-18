import json


def save2file(file, data):
    file.seek(0)
    file.truncate()
    json.dump(data, file)


def f_energy_boot(loras, energy_path):
    energy_file = open(energy_path, 'r+')
    energy_dic = json.load(energy_file)
    for lora_edges in loras:
        for slave in lora_edges['slaves']:
            id_meter = (lora_edges['loraid']).to_bytes(
                2, 'big') + (slave).to_bytes(1, 'big')  #
            if id_meter.hex() not in energy_dic.keys():
                energy_dic[id_meter.hex()] = 0
        print("Energy updated ", energy_dic)
        save2file(energy_file, energy_dic)
    energy_file.close()


def f_post_boot(loras, post_path):
    post_file = open(post_path, 'r+')
    post_dic = json.load(post_file)
    print("post dic", post_dic)
    updates = post_dic['updates']
    print(updates)
    for lora_edges in loras:
        for slave in lora_edges['slaves']:
            id_meter = (lora_edges['loraid']).to_bytes(
                2, 'big') + (slave).to_bytes(1, 'big')
            print("idmeter: ", id_meter.hex())
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
                print("appending ", updates)
    post_dic['updates'] = updates
    save2file(post_file, post_dic)
    post_file.close()
