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
    elif command == "2":
        print ("up_released")
        
    #dpad down commands
    elif command == "3":
        print ("down_pressed")
    elif command == "4":
        print ("down_released")
        
    #dpad left commands
    elif command == "5":
        print ("left_pressed")
    elif command == "6":
        print ("left_released")
        
    #dpad right commands
    elif command == "7":
        print ("right_pressed")
    elif command == "8":
        print ("right_released")

    #manual commands
    elif command == "9":
        print ("manual_pressed")
    elif command == "10":
        print ("manual_released")

    #auto commands
    elif command == "11":
        print ("auto_pressed")
    elif command == "12":
        print ("auto_released")    


BluetoothServer(data_received)
pause()

