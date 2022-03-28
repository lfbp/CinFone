import socket
import MainServer
PORT = 5050
BUFFER_SIZE = 2048
SERVER = MainServer.SERVER
ADDR = (SERVER, PORT)

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
print("sending initial message to server")
client.sendto("initial message".encode(), ADDR)
