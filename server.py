from audioop import add
import socket
import threading

PORT = 5050
BUFFER_SIZE = 2048
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = "utf-8"


def handleClient(msg, conn):
    print("Message from client: " + str(msg.decode(FORMAT)))


print("Server address is " + SERVER)
print("Creating udp socket and binding to " +
      str(ADDR[0]) + ", " + str(ADDR[1]))
server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind(ADDR)
print("Starting accepting connections")
while True:
    print("Waiting client connction...")
    msg, conn = server.recvfrom(BUFFER_SIZE)
    newThead = threading.Thread(target=handleClient, args=(msg, conn))
    newThead.start()
