from distutils.command.build_py import build_py_2to3
from email import message
from pydoc import cli
import socket
import struct
import ctypes
import sunau

FORMAT = "utf-8"
PORT = 5050
BUFFER_SIZE = 2048
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
WAIT_CALL_0 = 0
WAIT_ACK_0 = 1
WAIT_CALL_1 = 2
ACK = "ACK"

sequentialNumber = 0
currentState = WAIT_CALL_0

def checksum(data):
    sum = 0
    for i in range(0,len(data),2):
        if i + 1 < len(data):
            byteValue = bytearray(2)
            byteValue[0] = (data[i]) 
            byteValue[1] = (data[i+1])
            value = int.from_bytes(byteValue, "big")           
            sum = (sum + value) % 65535
        else:
            byteValue = bytearray(2)
            byteValue[0] = (data[i]) 
            byteValue[1] = 0
            value = int.from_bytes(byteValue, "big")            
            sum = (sum + value) % 65535
    sum = ~sum
    sum = (sum + 2**32) % 65535
    return sum 


def getSequencialNumber():
    global sequentialNumber
    number = sequentialNumber
    sequentialNumber = (sequentialNumber + 1) % 2
    return number

def send(message):
    packet = message.encode()
    datalen = len(packet)
    checksumValue = checksum(packet)
    sequentialNumber = getSequencialNumber()
    header = struct.pack("!III", datalen, checksumValue,sequentialNumber)
    headerPlusMessage = header + packet
    client.sendto(headerPlusMessage, ADDR)


client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

while True:
    if currentState == WAIT_CALL_0:
        message = input("send message: ")
        send(message)
        currentState = WAIT_ACK_0
    elif currentState == WAIT_ACK_0:
        print("waiting for ACK 0")
        ack, conn = client.recvfrom(BUFFER_SIZE)
        ack = str(ack.decode(FORMAT))
        if ack == ACK:
            print("ACK RECIEVED")
            currentState = WAIT_CALL_0
    elif currentState == WAIT_CALL_1:
        print("implement wait for above call 1")
        break



