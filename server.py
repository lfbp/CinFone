import socket
import threading

PORT = 5050
BUFFER_SIZE = 2048
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = "utf-8"


def handleClient(msg, conn):
    print("Message from client: " + str(msg.decode(FORMAT)))


print("Server ip is " + SERVER)

print("Creating socket...")
server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

print("Binding to " + str(ADDR[0]) + ", " + str(ADDR[1]))
server.bind(ADDR)

print("Starting receving connections")
while True:
    print("Waiting client connction...")
    msg, conn = server.recvfrom(BUFFER_SIZE)
    newThead = threading.Thread(target=handleClient, args=(msg, conn))
    newThead.start()
