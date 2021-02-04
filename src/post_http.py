import json
import requests
import time
import datetime
import sys

thing_speak = {    "write_api_key": "PYF7YMZNOM3TJVSM",
                        "updates": [{
                                    "created_at": "2020-10-30 13:38:2 -0400",
                                    "field1": 0,
                                    "field2": 0
                                    }
                                    ]    
            }
def post_thingS(data):
    print("posting...")
    now = datetime.datetime.now()
    now = str(now) + " -0400"
    print(now)
    update_data = thing_speak['updates'][0]
    update_data['created_at'] = now
    update_data['field1'] = data['000201']
    update_data['field2'] = data['000202']
    thing_speak['updates'][0] = update_data
    print(thing_speak)
    headers = {'Content-type': 'application/json'}
    r = requests.post('https://api.thingspeak.com/channels/1212777/bulk_update.json', json=thing_speak, headers=headers)
    print("Status code is :", r.status_code)        
 
def post_json(file):
    headers = {'Content-type': 'application/json'}
    try:
        r = requests.post('https://glacial-beach-93230.herokuapp.com/api/data', json=file, headers=headers)
        print("Status code is :", r.status_code)
        print(r)
        return r.status_code
    except Exception:
        print("Problems?", sys.exc_info())
        return 0
        
def post_scada(data_dic):
    print("Posting to Scada")
    print("Data to post: ", data_dic)
    r_code = post_json(data_dic)
       
    if r_code ==200:
        the_file=open("../output/send_later.txt","w+")
        lines = the_file.readlines()
        count = 0
        for line in lines:
            count += 1
            print("Line{}: {}".format(count, line))
            dic= json.loads(line)
            post_json(dic)
        the_file.seek(0)
        the_file.truncate()
        the_file.close()
            
    else:
        print("No internet")
        text = json.dumps(data_dic)+"\n"
        with open("../output/send_later.txt","a") as the_file:
            the_file.write(text)
        the_file.close()
    
    
if __name__== "__main__":

    print("Start")
    dic ={"id": "0001", "write_api_key": "PYF7YMZNOM3TJVSM", "updates": [{"meterid": "000201", "energy": 0, "date": "2021-01-21 12:11:26.090530 -0400"}, {"meterid": "000202", "energy": 0, "date": "2021-01-21 12:11:26.090768 -0400"}, {"meterid": "000200", "energy": 8, "date": "2021-01-05 13:24:38.587472 -0400"}]}
    post_scada(dic)