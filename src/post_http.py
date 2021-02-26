import json
import sys

import requests



def post_json(file):
    headers = {'Content-type': 'application/json'}
    try:
        r = requests.post('https://glacial-beach-93230.herokuapp.com/api/data',
                          json=file,
                          headers=headers)
        print("Status code is :", r.status_code)
        print(r)
        return r.status_code
    except Exception:
        print("Problems?", sys.exc_info())
        return 0


def post_scada(post_path):
    print("Posting to Scada")
    with open(post_path, 'r+') as post_file:
        data_dic = json.load(post_file)
        print("Data to post: ", data_dic)
        r_code = post_json(data_dic)

        if r_code == 200:
            with open("output/send_later.txt", "w+") as file:
                lines = file.readlines()
                count = 0
                for line in lines:
                    count += 1
                    print("Line{}: {}".format(count, line))
                    dic = json.loads(line)
                    post_json(dic)
                file.seek(0)
                file.truncate()

        else:
            print("No internet")
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
