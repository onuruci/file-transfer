import socket
import os
 

localIP     = ""

localPort   = 20001

bufferSize  = 1024

DIR_NAME = "../../objects/"

 

msgFromServer       = "Hello UDP Client"

bytesToSend         = str.encode(msgFromServer)


 

# Listen for incoming datagrams


def run_server():

    UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

    UDPServerSocket.bind((localIP, localPort))


    while(True):

        bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)

        message = bytesAddressPair[0]

        address = bytesAddressPair[1]

        clientMsg = "Message from Client:{}".format(message)
        clientIP  = "Client IP Address:{}".format(address)

        print(clientMsg)
        print(clientIP)



        # Sending a reply to client
        i = 0

        while(i < 1000):
            bytesToSend = str(i).encode('utf-8')

            UDPServerSocket.sendto(bytesToSend, address)

            receiveMsgPair = UDPServerSocket.recvfrom(bufferSize)

            receiveMsg = receiveMsgPair[0].decode('utf-8')

            if(receiveMsg == 'ACK'):
                i+=1




if __name__ == "__main__":
    run_server()

