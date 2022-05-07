import socket
import threading
import struct
import common

PORT = 8080
BUFFER_SIZE = 2048
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = "utf-8"
ACK = "ACK"

expected_sequence = 0
last_acked_sequence = 2
current_sequence = 0

#chatbot
current_state = 0

state_0 = 0
state_1 = 0

ESTADO_0 = 0
ESTADO_1 = 1

RECEBER_MESA = 1
RECEBER_NOME = 2

CONTA_INDIVIDUAL = 1
CONTA_MESA = 2
PAGAR = 3
CARDAPIO = 4
PEDIR = 5
SAIR = 6

numero_mesa = ""
nome = ""

print("Server ip is " + SERVER)
print("Creating socket...")
server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
print("Binding to " + str(ADDR[0]) + ", " + str(ADDR[1]))
server.bind(ADDR)

tableList = []
cardapio = [{"item": "Espetinho", "itemNumber": "1","price": 20.00}, {"item": "Espetinho", "itemNumber": "2","price": 20.00}]

# chatbot data
class table: 
    def __init__(self, accountList, tableNumber): 
        self.accountList = [accountList]
        self.tableNumber = tableNumber

class accountList: 
    def __init__(self, id, tableNumber, socket, orderList): 
        self.id = id 
        self.tableNumber = tableNumber
        self.socket = socket 
        self.orderList = [orderList]

class orderList: 
    def __init__(self, id, itemName, itemPrice): 
        self.id = id
        self.itemName = itemName 
        self.itemPrice = itemPrice

def createTable(name, tableNumber):
    account = accountList(name, tableNumber, 1, [])
    tableList.append(table([account], tableNumber))

def enviarCardapio():
    #enviar um item do cardápio por linha
    for item in cardapio:
        send(item.itemNumber+"- "+item.item+" - R$"+item.price, ADDR)

def pedirPedido(socket, message):
    for table in tableList:
        accountList = table.accountList
        for account in accountList:
            if account.socket == socket:
                item = filter(lambda item: item.itemNumber == message, cardapio)
                orderList = orderList(message, item.first.item, item.first.price)
                account.orderList.append(orderList)

def obterContaIndividual(socket):
    for table in tableList:
        clientSum = 0
        accountList = table.accountList
        send("Nome: "+accountList.id, ADDR)
        for account in accountList:
            if account.socket == socket:
                for order in account.orderList:
                    clientSum += order.itemPrice
                    send(order.itemName+" => R$"+order.itemPrice)
                send("Total: R$"+clientSum)

def obterContaMesa():
    generalSum = 0
    for table in tableList:
        clientSum = 0
        accountList = table.accountList
        send("Nome: "+accountList.id, ADDR)
        for account in accountList:
            for order in account.orderList:
                clientSum += order.itemPrice
                send(order.itemName+" => R$"+order.itemPrice)
            send("Total: R$"+clientSum)
            generalSum += clientSum
    send("Total da mesa: R$"+generalSum)

def finalizarConta(socket):
    for table in tableList:
        accountList = table.accountList
        for account in accountList:
            if account.socket == socket:
                accountList.remove(account)
        


def handleStateZero(message):
    if state_0 == 0:
        send("Digite sua mesa: ", ADDR)
        state_0 = RECEBER_MESA
    elif state_0 == RECEBER_MESA:
        numero_mesa = message
        send("Digite seu nome: ", ADDR)
        state_0 = RECEBER_NOME
    elif state_0 == RECEBER_NOME:
        nome = message
        createTable(nome, numero_mesa)
        state_0 = 0
        current_state = ESTADO_1        
    
def handleStateOne(message):
    if state_1 == CONTA_INDIVIDUAL:
        send("Digite sua mesa: ", ADDR)
    #elif state_1 == CARDAPIO:


def handleChatbot(msgOption):
    if current_state == ESTADO_0:
        handleStateZero(msgOption)
    elif current_state == ESTADO_1:
        handleStateOne(msgOption)


# Aux Functions
def handleClient(msg, clientCheckSum, sequence_number, addr):
    global expected_sequence
    global last_acked_sequence

    print("Message from client: " + msg.decode(FORMAT))
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
        handleChatbot(msg.decode(FORMAT))

def send(message, addr):
    packet = message.encode()
    datalen = len(packet)
    checksumValue = common.generateCheckum(packet)
    header = struct.pack("!III", datalen, checksumValue, sequence_number)
    headerPlusMessage = header + packet
    server.sendto(headerPlusMessage, addr)

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

# Main loop
while True:
    print("\nWaiting client connection...")
    fullPacket, conn = server.recvfrom(BUFFER_SIZE)
    data, header = decodeData(fullPacket)
    checksum = header[1]
    sequence_number = header[2]
    handleClient(data, checksum, sequence_number, conn)
