import serial
from _curses import baudrate
import array as arr
import time
nodos=[[0],[1,2,3],[1 ,2]]
def init_serial_port():
    try:
        ser = serial.Serial('/dev/ttyUSB2',timeout=3)
    except:
        print("Serial port does not exists")
        return
    print("Port ",ser.name," opened")
    ser.close
    print("port closed")
def poll_loras():
    
    for lora,slaves in enumerate(nodos):
        if len(slaves)==1 and slaves[0]==0:
            print("Empty")
            continue
        else:
            print(slaves)
            adu=[0]
            print(adu)
            adu.append(lora)   
            quantity =len(slaves)
            adu.append(quantity)
            print(adu)

if __name__ == "__main__":
    print("Hello World")
    init_serial_port()
    poll_loras()
    
    
    
