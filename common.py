def generateCheckum(data):
    sum = 0
    for i in range(0,len(data),2):
        if i + 1 < len(data):
            byteValue = bytearray(2)
            byteValue[0] = (data[i]) 
            byteValue[1] = (data[i+1])
            value = int.from_bytes(byteValue, "big")    
            sum = (sum + value) % 65535
        else:
            byteValue = bytearray(2)
            byteValue[0] = (data[i]) 
            byteValue[1] = 0
            value = int.from_bytes(byteValue, "big")    
            sum = (sum + value) % 65535
    sum = ~sum
    sum = (sum + 2**32) % 65535
    return sum 

def corrupted(data, received_checksum):
    checksum = generateCheckum(data)
    return checksum != received_checksum