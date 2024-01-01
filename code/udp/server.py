import socket
import os
import math
import time
 

localIP     = ""

localPort   = 20001

bufferSize  = 1024

DIR_NAME = "../../objects/"

 
header_length = 8
packet_data_length = 1016

msgFromServer       = "Hello UDP Client"

bytesToSend         = str.encode(msgFromServer)


## read file

def read_file(filename):
    with open(DIR_NAME + filename) as file:
        file_data = file.read()

        return file_data



# send data for sure

def send_data(s, data, address):
    while(True):
        s.sendto(data, address)

        receive = s.recvfrom(bufferSize)

        msg = receive[0].decode('utf-8')

        if(msg == 'ACK'):
            break



# handle send file


def send_file(filename, UDPServerSocket, address):
    filesize = os.path.getsize(DIR_NAME + filename)
    md5_data = read_file(filename+".md5").replace("\n", "")
    packet_count = int(math.ceil(filesize / float(packet_data_length)))

    metadata = (f"|{filename}|{filesize}|{md5_data}|{packet_count}|").encode("utf-8")

    # sending metadata
    send_data(UDPServerSocket, metadata, address)

    # start sending the file itself
    data_count = 0
    with open(DIR_NAME + filename) as file:
        i = 0
        while i < packet_count:
            window_size = 0
            sent_arr = [""] * 100
            for k in range(100):
                file_data = file.read(1016)

                if(not file_data):
                    break

                window_size += 1

                file_header = str(data_count) + "|"

                file_header = (8-len(file_header)) * "0" + file_header

                data_to_send = str(file_header+file_data).encode('utf-8')
                sent_arr[k] = data_to_send

                UDPServerSocket.sendto(data_to_send, address)

                data_count += 1

            received_acks = [0] * window_size
            i+= window_size
            while True:
                receive = UDPServerSocket.recvfrom(bufferSize)
                msg = receive[0].decode('utf-8')
                [msg_type, seq] = msg.split("|")

                seq = int(seq)
                received_acks[seq] = 1

                if(received_acks.count(0) == 0):
                    break

            print(f"Passing window {i}")




def run_server():

    UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

    UDPServerSocket.bind((localIP, localPort))


    while(True):
        bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)

        address = bytesAddressPair[1]

        clientIP  = ("Client connected with IP Address:{}".format(address))

        print(clientIP)

        start_time = time.time()
        for i in range(10):
            filename = "small-"+str(i)+".obj"

            send_file(filename, UDPServerSocket, address)
            print(f"{filename} sent successfully!")

            filename = "large-"+str(i)+".obj"

            send_file(filename, UDPServerSocket, address)
            print(f"{filename} sent successfully!")
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Execution time {elapsed_time}")








if __name__ == "__main__":
    run_server()

