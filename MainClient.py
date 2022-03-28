from distutils.command.build_py import build_py_2to3
import socket
import struct
import ctypes

PORT = 5050
BUFFER_SIZE = 2048
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)

def checkSumSender(data):
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
    sum = ~sum
    sum = sum + (1 << 32)
    return int.from_bytes(sum.to_bytes(4,byteorder='big'), byteorder='big') 


client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
message = "Hello Server"
packet = message.encode()
datalen = len(packet)
checksum = checkSumSender(packet)
header = struct.pack("!II", datalen, checksum)
headerPlusMessage = header + packet
print("Sending: " + message)
print(f"checksum equal to: {checksum}")
client.sendto(headerPlusMessage, ADDR)
