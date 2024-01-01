import socket



msgFromClient       = "Hello UDP Server"

bytesToSend         = str.encode(msgFromClient)

serverAddressPort   = ("172.17.0.2", 20001)

bufferSize          = 1024



def run_client():


    # Create a UDP socket at client side

    UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)



    # Send to server using created UDP socket

    UDPClientSocket.sendto(bytesToSend, serverAddressPort)

    i = 0

    while(i < 1000):

        msgFromServer = UDPClientSocket.recvfrom(bufferSize)



        msg = int(msgFromServer[0].decode('utf-8'))

        if(msg != i):
            UDPClientSocket.sendto(str.encode("NACK"), serverAddressPort)
            print(f"Missing {i}")
            print(msg)
        else:
            UDPClientSocket.sendto(str.encode("ACK"), serverAddressPort)
            print(f"Received {i}")
            print(msg)
            i+=1



if __name__ == "__main__":
    run_client()

