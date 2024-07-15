import threading
from queue import Queue

def getData(out_q):
    import socket
    import struct

    # Define the UDP IP address and port to listen on
    UDP_IP = "127.0.0.1"
    UDP_PORT = 20777

    def getVal(pos):
        data, addr = sock.recvfrom(1024)
        return struct.unpack('f', data[pos:pos + 4])[0]

    
    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))
    
    print(f"Listening for UDP packets on {UDP_IP}:{UDP_PORT}")
    pos = 148
    lastval = 0.0

    while True:
        
        
        rpm = getVal(pos)
        maxrpm = getVal(252)
        gear = getVal(132)



        out_q.put([rpm * 10, maxrpm * 10, gear, ])


def arduinoControl(in_q):
    import pyfirmata2
    import time
    
    firstStart = False
    

    print("aa") 
    board = pyfirmata2.Arduino('/dev/ttyACM0') 
    
    # initializing the LEDs 
    led1 = board.get_pin('d:10:o') 
    led2 = board.get_pin('d:11:o') 
    led3 = board.get_pin('d:12:o') 
    
    segA = board.get_pin('d:03:o')
    segB = board.get_pin('d:07:o')
    segC = board.get_pin('d:04:o')
    segD = board.get_pin('d:05:o')
    segE = board.get_pin('d:06:o')
    segF = board.get_pin('d:08:o')
    segG = board.get_pin('d:02:o')
    
    
    led1.write(False)
    led2.write(False)
    led3.write(False)
    

    LCD_PRINT = 0x04
    LCD_CLEAR = 0x05
    LCD_SET_CURSOR = 0x06


    def ledControl(q, start):
        while True:
            data = q.get()
            led1func(data)
            led2func(data)
            led3func(data)
            segDisp(data)
            displayRPM(data, start)

    def ledMsg(value, x, y):

        message_bytes = [ord(char) for char in value]
        board.send_sysex(LCD_SET_CURSOR, [x, y])
        board.send_sysex(LCD_PRINT, message_bytes)

    def clearLCD():
        board.send_sysex(LCD_CLEAR, [])
            
    def led1func(data):
        
        if ((data[0] > data[1] * 0.40) & (data[0] < data[1] * 0.70)):
            led1.write(True)
        else:
            led1.write(False)
                
    def led2func(data):
        
        if ((data[0] > data[1] * 0.70) & (data[0] < data[1] * 0.98)):
            led2.write(True)
        else:
            led2.write(False)
            
    def led3func(data):
        
        if (data[0] > data[1] * 0.98):
            led3.write(True)
        else:
            led3.write(False)


    def segDisp(data):            
        match data[2]:
            case 0:
                segA.write(True)
                segB.write(True)
                segC.write(True)
                segD.write(False)
                segE.write(True)
                segF.write(True)
                segG.write(False)
            case 1:
                segA.write(False)
                segB.write(True)
                segC.write(True)
                segD.write(False)
                segE.write(False)
                segF.write(False)
                segG.write(False)
            case 2:
                segA.write(True)
                segB.write(True)
                segC.write(False)
                segD.write(True)
                segE.write(True)
                segF.write(False)
                segG.write(True)
            case 3:
                segA.write(True)
                segB.write(True)
                segC.write(True)
                segD.write(True)
                segE.write(False)
                segF.write(False)
                segG.write(True)
            case 4:
                segA.write(False)
                segB.write(True)
                segC.write(True)
                segD.write(False)
                segE.write(False)
                segF.write(True)
                segG.write(True)
            case 5:
                segA.write(True)
                segB.write(False)
                segC.write(True)
                segD.write(True)
                segE.write(False)
                segF.write(True)
                segG.write(True)
            case 6:
                segA.write(True)
                segB.write(False)
                segC.write(True)
                segD.write(True)
                segE.write(True)
                segF.write(True)
                segG.write(True)
            case 7:
                segA.write(True)
                segB.write(True)
                segC.write(True)
                segD.write(False)
                segE.write(False)
                segF.write(False)
                segG.write(False)
            case -1:
                segA.write(True)
                segB.write(False)
                segC.write(False)
                segD.write(False)
                segE.write(True)
                segF.write(True)
                segG.write(False)

    def displayRPM(data, firstStart):
        if (firstStart == False):
            ledMsg(str(int(data[0])) + " RPM", 0, 0)
            clearLCD()
            ledMsg(str(int(data[0])) + " RPM", 0, 0)
            firstStart = True
        else:
            ledMsg(str(int(data[0])) + " RPM", 0, 0)


    


    tLedCont = threading.Thread(None, target=ledControl, args=(in_q, firstStart))
    

    tLedCont.start()    
    

    
    



        

        
        
        





q = Queue()
tData = threading.Thread(None, target = getData, args = (q, ))
tArduinoControl = threading.Thread(None, target = arduinoControl, args = (q, ))



tData.start()
tArduinoControl.start()

