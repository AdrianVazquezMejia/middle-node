import json
import sys
import logging
import requests
from distutils.log import debug

log = logging.getLogger('post')
ch = logging.NullHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
log.addHandler(ch)


def post_json(file, is_production):
    """! Get the status of the data

    @param file             dictionary to assign in the json
    @param is_production    chech if there is a new data to add

    @return success or error code    
    """
    headers = {'Content-type': 'application/json'}
    scada_url = 'https://postman-echo.com/post'
    if is_production:
        scada_url = "https://apimedidores.ciexpro.com/api/push/custom_create/"
    log, debug(scada_url)
    try:
        r = requests.post(scada_url, json=file, headers=headers)
        log.info("Status code is : %s", str(r.status_code))
        log.debug(str(r))
        return r.status_code
    except requests.exceptions.ConnectionError:
        log.error("Connection Error!")
    except Exception:
        log.error("Problems? %s", str(sys.exc_info()))
    return 0


def post_scada(data_dic, is_production):
    """! Create a text file with meters information

    @param data_dic         dictionary with meters' information
    @param is_production    chech if there is a new data to add      
    """
    log.info("Posting to Scada")
    success_code = 201
    log.debug("Data to post: %s", str(data_dic))
    r_code = post_json(data_dic, is_production)

    if r_code == success_code:
        with open("output/send_later.txt", "w+") as file:
            lines = file.readlines()
            count = 0
            for line in lines:
                count += 1
                log.debug("Line{}: {}".format(count, line))
                dic = json.loads(line)
                post_json(dic)
            file.seek(0)
            file.truncate()
    else:
        log.error("Post unsuccessful")
        text = json.dumps(data_dic) + "\n"
        with open("output/send_later.txt", "a") as file:
            file.write(text)
        file.close()


class MeterUpdate(object):
    def __init__(self, object_dic):
        self.lora_id = int(object_dic["meter"][0:4], 16)
        self.address = int(object_dic["meter"][4:6], 16)
        if self.address == 0:
            self.address = self.lora_id
        if "power" in object_dic:
            self.function = "Relay"
            self.value = object_dic["power"]
        else:
            self.function = "Reset"
            self.value = True


def get_meter_updates():
    #get json from cloud

    update_endpoint = "https://apimedidores.ciexpro.com/api/meter_conection/reconnect"
    location = "Estelio_CA"
    PARAMS = {'address': location}

    r = requests.get(url=update_endpoint, params=PARAMS)
    status_dic = r.json()
    print(status_dic)
    updates = status_dic["meters"]
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
        print(update["power"])

    return updates_list


if __name__ == "__main__":
    """! Main program entry
    
    """
    print("Start")
    aux_dic = {
        "id":
        "0001",
        "write_api_key":
        "PYF7YMZNOM3TJVSM",
        "updates": [{
            "meterid": "000201",
            "energy": 0,
            "date": "2021-01-21 12:11:26.090530 -0400"
        }, {
            "meterid": "000202",
            "energy": 0,
            "date": "2021-01-21 12:11:26.090768 -0400"
        }, {
            "meterid": "000200",
            "energy": 8,
            "date": "2021-01-05 13:24:38.587472 -0400"
        }]
    }
    #post_scada(aux_dic)
    print(get_meter_updates())
