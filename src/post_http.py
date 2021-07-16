import json
import sys
import logging
import requests
from distutils.log import debug

log = logging.getLogger('post')
ch = logging.NullHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
log.addHandler(ch)

def post_json(file, is_production):
    headers = {'Content-type': 'application/json'}
    scada_url = 'https://postman-echo.com/post'
    if is_production:
        scada_url = "https://apimedidores.ciexpro.com/api/push/custom_create/" 
    log,debug(scada_url)
    try:
        r = requests.post(scada_url,
                          json=file,
                          headers=headers)
        log.info("Status code is : %s", str(r.status_code))
        log.debug(str(r))
        return r.status_code
    except requests.exceptions.ConnectionError:
        log.error("Connection Error!")
    except Exception:
        log.error("Problems? %s", str(sys.exc_info()))
    return 0


def post_scada(post_path, is_production):
    log.info("Posting to Scada")
    success_code =201
    with open(post_path, 'r+') as post_file:
        data_dic = json.load(post_file)
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


if __name__ == "__main__":

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
    post_scada(aux_dic)
