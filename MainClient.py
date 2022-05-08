import socket
import threading
import struct
import common

SERVER_PORT = 8080
CLIENT_PORT = 5050

BUFFER_SIZE = 2048
HOST_NAME = socket.gethostbyname(socket.gethostname())
CLIENT_ADDR = (HOST_NAME, CLIENT_PORT)
SERVER_ADDR = (HOST_NAME, SERVER_PORT)

FORMAT = "utf-8"
ACK = "ACK"

expected_sequence = 0
last_acked_sequence = 2

WAIT_CALL = 0
WAIT_ACK = 1
TIMEOUT = 2
CORRUPT = 3
DUPLICATE_ACK = 4
WAIT_RESPONSE = 5

sent_message = ""
current_sequence = 0
current_state = WAIT_CALL#WAIT_RESPONSE

print("Server ip is " + HOST_NAME)
print("Creating socket...")
server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
print("Binding to " + str(CLIENT_ADDR[0]) + ", " + str(CLIENT_ADDR[1]))
server.bind(CLIENT_ADDR)

# Aux Functions
def send(message, addr):
    packet = message.encode()
    datalen = len(packet)
    checksumValue = common.generateCheckum(packet)
    header = struct.pack("!III", datalen, checksumValue, current_sequence)
    headerPlusMessage = header + packet
    print("Send to ", addr)
    server.sendto(headerPlusMessage, addr)
    print("Sent")


def handleClient(msg, clientCheckSum, sequence_number, addr):
    global expected_sequence
    global last_acked_sequence

    print(msg.decode(FORMAT))

    if common.corrupted(msg, clientCheckSum):
        print("CORRUPTED, ACK Previous: ", last_acked_sequence)
        sendACK(addr, last_acked_sequence)

    elif sequence_number != expected_sequence:
        print("Unexpected sequence number")
        sendACK(addr, last_acked_sequence)
    
    else:
        sendACK(addr, expected_sequence)
        last_acked_sequence = sequence_number
        expected_sequence = (sequence_number + 1) % 2

def sendACK(addr, sequence_number):
    packet = "ACK".encode()
    datalen = len(packet)
    checksumValue = common.generateCheckum(packet)
    header = struct.pack("!III", datalen, checksumValue, sequence_number)
    headerPlusMessage = header + packet
    server.sendto(headerPlusMessage, addr)

def decodeData(fullPacket):
    udpHeader = fullPacket[:12]
    data = fullPacket[12:]
    header = struct.unpack("!III", udpHeader)
    return data, header

while True:
    if current_state == WAIT_CALL:
        sent_message = input("Send message: ")
        send(sent_message, SERVER_ADDR)
        current_state = WAIT_ACK

    elif current_state == WAIT_RESPONSE:
        fullPacket, conn = server.recvfrom(BUFFER_SIZE)
        data, header = decodeData(fullPacket)
        checksum = header[1]
        sequence_number = header[2]
        handleClient(data, checksum, sequence_number, conn)
        current_state = WAIT_CALL

    elif current_state == WAIT_ACK:
        try:
            fullPacket, conn = server.recvfrom(BUFFER_SIZE)
            data, header = decodeData(fullPacket)
            checksum = header[1]
            seq = header[2]
            message = data.decode(FORMAT)

            if message != "ACK" or common.corrupted(data, checksum):                
                current_state = CORRUPT

            elif seq != current_sequence:
                current_state = DUPLICATE_ACK

            else:
                current_state = WAIT_RESPONSE
                current_sequence = (current_sequence + 1) % 2
                continue    
        except socket.timeout as e:
            current_state = TIMEOUT

    elif current_state == TIMEOUT:
        print("Timed Out, ACK " + str(current_sequence) + " not received")
        send(sent_message, SERVER_ADDR)
        print("Message Recent")
        current_state = WAIT_ACK

    elif current_state == CORRUPT:
        print("Corrupt Message") #dbg
        send(sent_message, SERVER_ADDR)
        print("Message Recent")
        current_state = WAIT_ACK #dbg

    elif current_state == DUPLICATE_ACK:
        print("Incorrect Sequence Received")
        current_state = WAIT_ACK 