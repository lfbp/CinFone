import socket
import struct
import time
import common

FORMAT = "utf-8"
PORT = 5050
BUFFER_SIZE = 2048
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
WAIT_CALL_0 = 0
WAIT_ACK_0 = 1
WAIT_CALL_1 = 2
WAIT_ACK_1 = 3
ACK = "ACK"
NACK = "NACK"
initialTime = time.perf_counter()

sequentialNumber = 0
currentState = WAIT_CALL_0

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Aux Functions
def getSequencialNumber():
    global sequentialNumber
    number = sequentialNumber
    sequentialNumber = (sequentialNumber + 1) % 2
    return number

def send(message, addr):
    packet = message.encode()
    datalen = len(packet)
    checksumValue = common.generateCheckum(packet)
    sequentialNumber = getSequencialNumber()
    header = struct.pack("!III", datalen, checksumValue,sequentialNumber)
    headerPlusMessage = header + packet
    client.sendto(headerPlusMessage, addr)

def isACK(ack):
    return ack == ACK

def decodeData(fullPacket):
    udpHeader = fullPacket[:12]
    data = fullPacket[12:]
    header = struct.unpack("!III", udpHeader)
    return data, header

# Main Loop
while True:
    if currentState == WAIT_CALL_0:
        message = input("send message: ")
        send(message, ADDR)
        currentState = WAIT_ACK_0
    elif currentState == WAIT_ACK_0:
        print("waiting for ACK 0...")
        client.settimeout(1.0)
        fullPacket, conn = client.recvfrom(BUFFER_SIZE)
        data, header = decodeData(fullPacket)
        checksum = header[1]
        seq = header[2]
        ack = data.decode(FORMAT)
        if isACK(ack) and not common.corrupted(data, checksum) and seq == 0:
            print("ACK 0 RECIEVED")
            #stop timer
            currentState = WAIT_CALL_1
            continue
    elif currentState == WAIT_CALL_1:
        message = input("send message: ")
        send(message, ADDR)
        initialTime = time.perf_counter()
        currentState = WAIT_ACK_1
    elif currentState == WAIT_ACK_1:
        print("waiting for ACK 1...")
        fullPacket, conn = client.recvfrom(BUFFER_SIZE)
        data, header = decodeData(fullPacket)
        checksum = header[1]
        seq = header[2]
        ack = data.decode(FORMAT)
        if isACK(ack) and not common.corrupted(data, checksum) and seq == 1:
            print("ACK 1 RECIEVED")
            #stop timer
            currentState = WAIT_CALL_0
            continue
