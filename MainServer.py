from operator import xor
import socket
import threading
import struct

PORT = 5050
BUFFER_SIZE = 2048
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = "utf-8"


def checkSumReceiver(data, checksum):
    sum = 0
    for i in range(0,len(data),2):
        if i + 1 < len(data):
            value = 0
            value = (data[i])
            value << 8
            value += data[i+1]                
            sum += value
        else:
            value = 0
            value = int(data[i])
            value << 8
            sum += value
    sum = sum + (1 << 32)
    sum = sum + checksum
    sum = sum ^ 0xfff
    return sum 

def handleClient(msg, clientCheckSum, conn):
    print("Message from client: " + str(msg.decode(FORMAT)))
    print(f"checkSumReceiver: {checkSumReceiver(msg, clientCheckSum)}, must be equal to {int('0x1fffff000', 0)}")


print("Server ip is " + SERVER)
print("Creating socket...")
server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

print("Binding to " + str(ADDR[0]) + ", " + str(ADDR[1]))
server.bind(ADDR)

print("Starting receving connections")
while True:
    print("")
    print("Waiting client connction...")
    full_packet, conn = server.recvfrom(BUFFER_SIZE)
    udp_header = full_packet[:8]
    data = full_packet[8:]
    udpHeader = struct.unpack("!II", udp_header)
    newThead = threading.Thread(target=handleClient, args=(data, udpHeader[1], conn))
    newThead.start()
    print("")
