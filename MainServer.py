import socket
import threading
import struct

PORT = 5050
BUFFER_SIZE = 2048
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = "utf-8"
ACK = "ACK"
sequentialNumber = 0

def corrupted(data, checksum):
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
    sum = (sum + checksum)
    return sum != int('0xFFFF', 0)

def generateCheckum(data):
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

def handleClient(msg, clientCheckSum, sequentialNumber, addr):
    print("Message from client: " + msg.decode(FORMAT))
    print(f'Message sequential number: {sequentialNumber}')
    corrupted(msg, clientCheckSum)
    if not corrupted(msg, clientCheckSum):
        send(ACK, addr)
    else:
        print("CORRUPTED")

def getSequencialNumber():
    global sequentialNumber
    number = sequentialNumber
    sequentialNumber = (sequentialNumber + 1) % 2
    return number

def send(message, addr):
    packet = message.encode()
    datalen = len(packet)
    checksumValue = generateCheckum(packet)
    sequentialNumber = getSequencialNumber()
    header = struct.pack("!III", datalen, checksumValue,sequentialNumber)
    headerPlusMessage = header + packet
    server.sendto(headerPlusMessage, addr)

def decodeData(fullPacket):
    udpHeader = fullPacket[:12]
    data = fullPacket[12:]
    header = struct.unpack("!III", udpHeader)
    return data, header


print("Server ip is " + SERVER)
print("Creating socket...")
server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
print("Binding to " + str(ADDR[0]) + ", " + str(ADDR[1]))
server.bind(ADDR)

while True:
    print("")
    print("Waiting client connction...")
    fullPacket, conn = server.recvfrom(BUFFER_SIZE)
    data, header = decodeData(fullPacket)
    checksum = header[1]
    sequentialNumber = header[2]
    # newThead = threading.Thread(target=handleClient, args=(data, udpHeader[1], udpHeader[2], conn))
    # newThead.start()
    handleClient(data, checksum, sequentialNumber, conn)
    print("")
