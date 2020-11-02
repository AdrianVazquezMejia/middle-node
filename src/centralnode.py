import json

class centralnode:
    def __init__(self, config_path):
        config_file=open(config_path,'r')
        config_dic=json.load(config_file)
        
        self.id = config_dic['ID']
        self.lora_port = config_dic['Serial Port']
        self.energy_path = config_dic['energy_path']
        self.loras = config_dic['loras']
        
        print("This node ID: ",config_dic['ID'])
        print("Lora Serial Port: ",config_dic['Serial Port'])
        print("Energy path: ",self.energy_path)
        
        self.lora_list = []
        
        for i in self.loras:
            #print(i)
            self.lora_list.append(i['loraid'])
        #print(self.lora_list)   
        config_file.close()
