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
current_state = WAIT_RESPONSE

print("Server ip is " + HOST_NAME)
print("Creating socket...")
server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
print("Binding to " + str(SERVER_ADDR[0]) + ", " + str(SERVER_ADDR[1]))
server.bind(SERVER_ADDR)


##### CHATBOT BEGIN
PERGUNTAR_MESA = 0
RECEBER_MESA = 1
RECEBER_NOME = 2
PERGUNTAR_MENU = 3
RECEBER_MENU = 4
RECEBER_PEDIDO = 5

current_chatbot_state = PERGUNTAR_MESA

numero_mesa = ""
nome = ""

tableList = []
cardapioItems = [{"item": "Espetinho", "itemNumber": "1","price": 20.00}, {"item": "Espetinho", "itemNumber": "2","price": 20.00}]

client_message = ""

class table: 
    def __init__(self, clients, tableNumber): 
        self.clients = clients
        self.tableNumber = tableNumber

class client: 
    def __init__(self, id, tableNumber, addr, orderList): 
        self.id = id 
        self.tableNumber = tableNumber
        self.addr = addr 
        self.orderList = orderList

class orderList: 
    def __init__(self, id, itemName, itemPrice): 
        self.id = id
        self.itemName = itemName 
        self.itemPrice = itemPrice

def createTable(name, tableNumber, addr):
    global tableList
    created_client = client(name, tableNumber, addr, [])
    created_table = table([created_client], tableNumber)
    tableList.append(created_table)
    print("Created Table, ", tableNumber)

def cardapio():
    print("CARDAPIO")
    #enviar um item do cardápio por linha
    message = ""
    for item in cardapioItems:
        message += item["itemNumber"]+"- "+item["item"]+" - R$"+str(item["price"])+"\n"
    return message

def pedir(addr, numeroDoProduto):
    print("Procurando cliente")
    for table in tableList:
        clients = table.clients
        for client in clients:
            if client.addr == addr:
                print("Cliente encontrado")
                product = next(filter(lambda item: item["itemNumber"] == numeroDoProduto, cardapioItems))
                print(product)
                created_orderList = orderList(message, product["item"], product["price"])
                client.orderList.append(created_orderList)
                return "Ok! Aqui está um " + product["item"]

    return "Produto não encontrado"

def obterContaIndividual(addr):
    print("CONTA INDIVIDUAL")
    message = ""
    for table in tableList:
        clientSum = 0
        clients = table.clients
        for client in clients:
            if client.addr == addr:
                for order in client.orderList:
                    clientSum += order.itemPrice
                    message += order.itemName+" => R$"+ str(order.itemPrice) + "\n"
                message += "\nTotal: R$"+ str(clientSum)
                return message

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

menu_message = "Digite uma das opções a seguir (o número ou por extenso)\n1 - cardápio\n2 - pedir\n3 - pagar\n4 - conta individual\n5 - conta da mesa\n6 - levantar da mesa"

def getResponse():
    global client_message
    global numero_mesa
    global nome
    global current_chatbot_state

    message = client_message.lower()

    print("STATE: ", current_chatbot_state)

    if current_chatbot_state == PERGUNTAR_MESA:
        current_chatbot_state = RECEBER_MESA
        return "Digite sua mesa"

    elif current_chatbot_state == RECEBER_MESA:
        numero_mesa = message
        current_chatbot_state = RECEBER_NOME
        return "Digite seu nome: "

    elif current_chatbot_state == RECEBER_NOME:
        nome = message
        createTable(nome, numero_mesa, CLIENT_ADDR)
        current_chatbot_state = RECEBER_MENU
        return menu_message

    elif current_chatbot_state == PERGUNTAR_MENU:
        return menu_message

    elif current_chatbot_state == RECEBER_MENU:
        print("RECEBER MENU")

        if(message == "1" or message == "cardapio" or message == "cardápio"):
            current_chatbot_state = RECEBER_MENU
            return cardapio()
        
        elif (message == "2" or message == "pedir"):
            current_chatbot_state = RECEBER_PEDIDO
            return "Digite o número do item desejado:"

        elif (message == "4" or message == "conta individual"):
            current_chatbot_state = RECEBER_MENU
            return obterContaIndividual(CLIENT_ADDR)

        else:
            return "Não entendi..."

    elif current_chatbot_state == RECEBER_PEDIDO:
        print("RECEBER PEDIDO")
        current_chatbot_state = RECEBER_MENU
        return pedir(CLIENT_ADDR, message)
    
    else:
        return "ERRO"

##### CHATBOT END

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
    global client_message

    print("Message from client: " + msg.decode(FORMAT))
    client_message = msg.decode(FORMAT)
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
        sent_message = getResponse()
        send(sent_message, CLIENT_ADDR)
        current_state = WAIT_ACK

    elif current_state == WAIT_RESPONSE:
        print("\nWaiting client connection...")
        fullPacket, conn = server.recvfrom(BUFFER_SIZE)
        data, header = decodeData(fullPacket)
        checksum = header[1]
        sequence_number = header[2]
        handleClient(data, checksum, sequence_number, conn)
        current_state = WAIT_CALL

    elif current_state == WAIT_ACK:
        print("waiting for ACK " + str(current_sequence) + "...")
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
                print("ACK " + str(current_sequence) + " RECIEVED")
                current_state = WAIT_RESPONSE
                current_sequence = (current_sequence + 1) % 2
                continue    
        except socket.timeout as e:
            current_state = TIMEOUT

    elif current_state == TIMEOUT:
        print("Timed Out, ACK " + str(current_sequence) + " not received")
        send(sent_message, CLIENT_ADDR)
        print("Message Recent")
        current_state = WAIT_ACK

    elif current_state == CORRUPT:
        print("Corrupt Message") #dbg
        send(sent_message, CLIENT_ADDR)
        print("Message Recent")
        current_state = WAIT_ACK #dbg

    elif current_state == DUPLICATE_ACK:
        print("Incorrect Sequence Received")
        current_state = WAIT_ACK 