import socket
import hashlib



msgFromClient       = "Hello UDP Server"

bytesToSend         = str.encode(msgFromClient)

serverAddressPort   = ("172.17.0.2", 20001)

bufferSize          = 1024

ACK = "ACK"
NACK = "NACK"

def get_md5(bytes_data):
    return hashlib.md5(bytes_data.encode('utf-8')).hexdigest()

def send_data(s, data):
    s.sendto(str.encode(data), serverAddressPort)

def send_response(s, data, n):
    s.sendto(str.encode(data + "|" + str(n)), serverAddressPort)

def recv_file(packet_count, UDPClientSocket):
    data = ""
    i = 0
    while i < packet_count:
        window_size = min(packet_count - i, 1000)
        received_arr = [""] * window_size
        while True:
            packet_received = UDPClientSocket.recvfrom(bufferSize)[0]

            packet_decoded = packet_received.decode('utf-8')

            [packet_no, packet_data] = packet_decoded.split('|')

            window_place = int(packet_no) % 1000

            send_response(UDPClientSocket, ACK, window_place)

            received_arr[window_place] = packet_data


            if(received_arr.count("") == 0):
                break

        i+=1000

        for j in range(window_size):
            data += received_arr[j]

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


def run_client():


    # Create a UDP socket at client side

    UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    UDPClientSocket.settimeout(1)


    # Send to server using created UDP socket

    UDPClientSocket.sendto(bytesToSend, serverAddressPort)

    for i in range(20):
        # recv metadata

        metadata = recv_metadata(UDPClientSocket)

        metadata_parsed = metadata.split("|")

        print(metadata)
        filename = metadata_parsed[0]
        filesize = metadata_parsed[1]
        checksum = metadata_parsed[2]
        packet_count = int(metadata_parsed[3])

        recv_file(packet_count, UDPClientSocket)

        print(checksum)




if __name__ == "__main__":
    run_client()

