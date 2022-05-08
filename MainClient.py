import socket
import struct
import time
import common

FORMAT = "utf-8"
PORT = 8080
BUFFER_SIZE = 2048
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)

WAIT_CALL = 0
WAIT_ACK = 1
TIMEOUT = 2
CORRUPT = 3
DUPLICATE_ACK = 4
WAIT_RESPONSE = 5
SHUT_DOWN = 6

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client.settimeout(1.0)

sent_message = ""
current_sequence = 0
current_state = WAIT_CALL
count_wait = 0


# Aux Functions

def send(message, addr):
    packet = message.encode()
    datalen = len(packet)
    checksumValue = common.generateCheckum(packet)
    header = struct.pack("!III", datalen, checksumValue, current_sequence)
    headerPlusMessage = header + packet
    client.sendto(headerPlusMessage, addr)

def decodeData(fullPacket):
    udpHeader = fullPacket[:12]
    data = fullPacket[12:]
    header = struct.unpack("!III", udpHeader)
    return data, header

# Main Loop
while True:
    print("")
    if current_state == WAIT_CALL:
        sent_message = input("Send message: ")
        send(sent_message, ADDR)
        current_state = WAIT_ACK
        count_wait = 0

    elif  current_state == WAIT_RESPONSE:
        print("waiting for response...")
        try:
            fullPacket, conn = client.recvfrom(BUFFER_SIZE)
            data, header = decodeData(fullPacket)
            checksum = header[1]
            seq = header[2]
            message = data.decode(FORMAT)

            if common.corrupted(data, checksum):                
                current_state = CORRUPT

            else:
                #LFBP: A PORRA DAS MSG DO SERVIDOR VÃO APARECE NA PORRA DESSA LINHA AQUI DE BAIXO
                print("SERVER RESPONSE: " + message)
                current_state = WAIT_CALL
                continue    
        except socket.timeout as e:
            current_state = TIMEOUT

    elif current_state == WAIT_ACK:
        print("waiting for ACK " + str(current_sequence) + "...")
        try:
            fullPacket, conn = client.recvfrom(BUFFER_SIZE)
            data, header = decodeData(fullPacket)
            checksum = header[1]
            seq = header[2]
            message = data.decode(FORMAT)

            if message != "ACK" or common.corrupted(data, checksum):                
                current_state = CORRUPT

            elif seq != current_sequence:
                current_state = DUPLICATE_ACK

            else:
                print("ACK " + str(current_sequence) + " RECIEVED")
                current_state = WAIT_RESPONSE
                current_sequence = (current_sequence + 1) % 2
                continue    
        except socket.timeout as e:
            current_state = TIMEOUT

    elif current_state == TIMEOUT:
        print("Timed Out, ACK " + str(current_sequence) + " not received")
        send(sent_message, ADDR)
        print("Message Resended")
        current_state = WAIT_ACK
        if count_wait > 5:
            print("WAITING FOR TO LONG... TIME TO GIVE UP")
            break
        else:
            count_wait += 1

    elif current_state == CORRUPT:
        print("Corrupt Message")
        send(sent_message, ADDR)
        print("Message Recent")
        current_state = WAIT_ACK

    elif current_state == DUPLICATE_ACK:
        print("Incorrect Sequence Received")
        current_state = WAIT_ACK 