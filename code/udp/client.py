import socket
import hashlib
from file import File


msgFromClient       = "connect"

bytesToSend         = str.encode(msgFromClient)

serverAddressPort   = ("172.17.0.2", 20001)

bufferSize          = 1024

ACK = "ACK"
NACK = "NACK"

SYS = "SYS"
SEND = "SEND"

server_state = SYS

file_arr = []
file_index = 0

def get_md5(bytes_data):
    return hashlib.md5(bytes_data.encode('utf-8')).hexdigest()

def send_data(s, data):
    s.sendto(str.encode(data), serverAddressPort)

def send_response(s, data, n, file_index):
    s.sendto(str.encode(data + "|" + str(n) + "|" + str(file_index)), serverAddressPort)

def recv_file(UDPClientSocket):
    while True:
        try:
            packet_received = UDPClientSocket.recvfrom(bufferSize)[0]

            packet_decoded = packet_received.decode('utf-8')

            if(packet_decoded.count('|') > 3):
                send_data(UDPClientSocket, ACK)
                continue


            [file_index, packet_no, packet_data] = packet_decoded.split('|')

            window_place = int(packet_no)
            file_index = int(file_index)


            file_arr[file_index].add_data(packet_data, window_place)

            send_response(UDPClientSocket, ACK, window_place, file_index)
        except socket.timeout:
            print("All files received terminating!")
            break







###################

def recv_metadata(UDPClientSocket):
    metadata_bytes = b""
    while(True):
        msgFromServer = UDPClientSocket.recvfrom(bufferSize)

        metadata_bytes += msgFromServer[0]

        metadata_str_temp = metadata_bytes.decode('utf-8')

        if(metadata_str_temp.count('|') == 5):
            print("Metadata fully received")
            send_data(UDPClientSocket, ACK)
            break
        else:
            print("Metadata not yet received")
            print(metadata_bytes)
            send_data(UDPClientSocket, NACK)


    metadata = metadata_bytes.decode('utf-8')[1:-1]
    return metadata

###################

def recv_all_metadata(UDPClientSocket):
    global file_arr
    global server_state
    metadata_bytes = b""
    metadata_all = []
    while(True):
        try:
            msgFromServer = UDPClientSocket.recvfrom(2048)

            metadata_bytes += msgFromServer[0]

            metadata_str_temp = metadata_bytes.decode('utf-8')

            if(metadata_str_temp.count('|') == 60):
                server_state = SEND
                print("Metadata fully received")
                send_data(UDPClientSocket, ACK)
                metadata_all = metadata_str_temp.split("*")
                break
        except socket.timeout:
            if(server_state == SYS):
                send_data(UDPClientSocket, ACK)


    for i in range(len(metadata_all)):
        metadata_parsed = metadata_all[i].split("|")
        filename = metadata_parsed[0]
        filesize = metadata_parsed[1]
        checksum = metadata_parsed[2]
        packet_count = int(metadata_parsed[3])


        file_arr += [File(filename, packet_count, filesize, checksum)]

    return
##################

def construct_files(metadata_all):
    global file_arr
    for i in range(len(metadata_all)):
        metadata_parsed = metadata_all[i].split("|")
        filename = metadata_parsed[0]
        filesize = metadata_parsed[1]
        checksum = metadata_parsed[2]
        packet_count = int(metadata_parsed[3])

        file_arr += [File(filename, packet_count, filesize, checksum)]
    
    print(f"Constructed {len(file_arr)} files")
    return



###################


def run_client():
    global file_arr
    global server_state
    metadata_all = []


    # Create a UDP socket at client side

    UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    UDPClientSocket.settimeout(0.5)


    # Send to server using created UDP socket
    while True:
        try:
            UDPClientSocket.sendto(bytesToSend, serverAddressPort)
            metadata_str_temp = UDPClientSocket.recvfrom(2048)[0].decode('utf-8')
            if(metadata_str_temp.count('|') == 60):
                server_state = SEND
                print("Metadata fully received")
                send_data(UDPClientSocket, ACK)
                metadata_all = metadata_str_temp.split("*")
                break

        except socket.timeout:
            print("No connection established yet looking for server")

    UDPClientSocket.settimeout(3)



    construct_files(metadata_all)
    #recv_all_metadata(UDPClientSocket)

    # recv metadata


    recv_file(UDPClientSocket)





if __name__ == "__main__":
    for i in range(30):
        file_arr = []
        server_state = SYS
        run_client()



