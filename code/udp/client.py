import socket
import hashlib
from file import File


msgFromClient       = "Hello UDP Server"

bytesToSend         = str.encode(msgFromClient)

serverAddressPort   = ("172.17.0.2", 20001)

bufferSize          = 1024

ACK = "ACK"
NACK = "NACK"

file_arr = []
file_index = 0

def get_md5(bytes_data):
    return hashlib.md5(bytes_data.encode('utf-8')).hexdigest()

def send_data(s, data):
    s.sendto(str.encode(data), serverAddressPort)

def send_response(s, data, n):
    s.sendto(str.encode(data + "|" + str(n)), serverAddressPort)

def recv_file(packet_count, UDPClientSocket):
    data = ""
    i = 0
    data_arr = [""] * packet_count
    while True:
        packet_received = UDPClientSocket.recvfrom(bufferSize)[0]

        packet_decoded = packet_received.decode('utf-8')

        [packet_no, packet_data] = packet_decoded.split('|')

        window_place = int(packet_no)

        data_arr[window_place] = packet_data

        send_response(UDPClientSocket, ACK, window_place)

        i += 1


        if(i >= packet_count):
            break

    for j in range(packet_count):
        data += data_arr[j]

    print("Calculating md5")
    md5 = get_md5(data)

    print(md5)


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
    metadata_bytes = b""
    metadata_all = []
    while(True):
        msgFromServer = UDPClientSocket.recvfrom(2048)

        metadata_bytes += msgFromServer[0]

        metadata_str_temp = metadata_bytes.decode('utf-8')

        if(metadata_str_temp.count('|') == 60):
            print("Metadata fully received")
            send_data(UDPClientSocket, ACK)
            metadata_all = metadata_str_temp.split("*")
            break
        else:
            print("Metadata not yet received")
            send_data(UDPClientSocket, NACK)

    for i in range(len(metadata_all)):
        metadata_parsed = metadata_all[i].split("|")
        filename = metadata_parsed[0]
        filesize = metadata_parsed[1]
        checksum = metadata_parsed[2]
        packet_count = int(metadata_parsed[3])

        file_arr += [File(filename, packet_count, filesize, checksum)]

    return



###################


def run_client():


    # Create a UDP socket at client side

    UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    UDPClientSocket.settimeout(3)


    # Send to server using created UDP socket

    UDPClientSocket.sendto(bytesToSend, serverAddressPort)

    recv_all_metadata(UDPClientSocket)

    for i in range(20):
        # recv metadata
        print(f"Running file {i}")
        curr_file = file_arr[i]

        checksum = curr_file.checksum
        packet_count = curr_file.packet_count

        recv_file(packet_count, UDPClientSocket)

        print(checksum)




if __name__ == "__main__":
    run_client()

