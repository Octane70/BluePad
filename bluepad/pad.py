import sys
sys.path.insert(0, "/home/pi/code/BluePad")
from bluedot.btcomm import BluetoothServer
from signal import pause

print ("bluepad test")

def data_received(data):
    command = data
    
    #dpad up commands
    if command == "1":
        print ("up_pressed")
    elif command == "0":
        print ("up_released")
    #dpad down commands
    elif command == "4":
        print ("down_pressed")
    elif command == "3":
        print ("down_released")


BluetoothServer(data_received)
pause()
