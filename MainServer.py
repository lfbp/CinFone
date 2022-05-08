import socket
import threading
import struct
import common

PORT = 5050
BUFFER_SIZE = 2048
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = "utf-8"
ACK = "ACK"

expected_sequence = 0
last_acked_sequence = 2

print("Server ip is " + SERVER)
print("Creating socket...")
server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
print("Binding to " + str(ADDR[0]) + ", " + str(ADDR[1]))
server.bind(ADDR)

# Aux Functions
def handleClient(msg, clientCheckSum, sequence_number, addr):
    global expected_sequence
    global last_acked_sequence

    print("Message from client: " + msg.decode(FORMAT))
    message = msg.decode(FORMAT)
    print(f'Received Sequence: {sequence_number}')
    print(f'Expected Sequence: {expected_sequence}')

    # Simulate Corrupted
    # clientCheckSum = clientCheckSum + 10

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
        #LFBP: DEPOIS DE MANDAR A PORRA DO ACK, VOCÊ PODE MANDAR AS MENSAGENS DE RESPOSTA AO CLIENTE
        #LFBP: É SÓ IR FAZEDO MAIS IF E MAIS ELSE AQUI EM BAIXO E IMPLEMENTAR AS REGRAS DE NEGÓCIO E TUDO MAIS
        #LFBP: TEM LÁ NO PROJETO AS FUNÇÕES OBRIGATÓRIAS E A REGRA DE NEGÓCIO ASSOCIADA
        if message == "Chefia":
            send("Digite número da mesa e nome no formato: mesa,nome.\nExemplo: 16,Luis Felipe.", addr)
        else:
            send("O comando enviado não foi reconhecido.", addr)

def sendACK(addr, sequence_number):
    packet = "ACK".encode()
    datalen = len(packet)
    checksumValue = common.generateCheckum(packet)
    header = struct.pack("!III", datalen, checksumValue, sequence_number)
    headerPlusMessage = header + packet
    server.sendto(headerPlusMessage, addr)

def send(message, addr):
    packet = message.encode()
    datalen = len(packet)
    checksumValue = common.generateCheckum(packet)
    header = struct.pack("!III", datalen, checksumValue, 100)
    headerPlusMessage = header + packet
    server.sendto(headerPlusMessage, addr)

def decodeData(fullPacket):
    udpHeader = fullPacket[:12]
    data = fullPacket[12:]
    header = struct.unpack("!III", udpHeader)
    return data, header


# Main loop
while True:
    print("\nWaiting client connection...")
    fullPacket, conn = server.recvfrom(BUFFER_SIZE)
    data, header = decodeData(fullPacket)
    checksum = header[1]
    sequence_number = header[2]
    handleClient(data, checksum, sequence_number, conn)
