import socket
import threading
import struct

PORT = 5050
BUFFER_SIZE = 2048
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = "utf-8"
ACK = "ACK"

def isCorrupted(data, checksum):
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
    return sum 

def handleClient(msg, clientCheckSum, sequentialNumber, conn):
    print("Message from client: " + str(msg.decode(FORMAT)))
    print(f'Message sequential number: {sequentialNumber}')
    checkSum = isCorrupted(msg, clientCheckSum)
    if checkSum == int('0xFFFF', 0):
        print("DATA NOT CORRUPTED, SENDING ACK...")
        server.sendto(ACK.encode(), conn)
    else:
        print("CORRUPTED")


print("Server ip is " + SERVER)
print("Creating socket...")
server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
print("Binding to " + str(ADDR[0]) + ", " + str(ADDR[1]))
server.bind(ADDR)

while True:
    print("Waiting client connction...")
    full_packet, conn = server.recvfrom(BUFFER_SIZE)
    udp_header = full_packet[:12]
    data = full_packet[12:]
    udpHeader = struct.unpack("!III", udp_header)
    # newThead = threading.Thread(target=handleClient, args=(data, udpHeader[1], udpHeader[2], conn))
    # newThead.start()
    handleClient(data, udpHeader[1], udpHeader[2], conn)
