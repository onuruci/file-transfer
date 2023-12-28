# echo-client.py

import socket
import hashlib

from utils import ACK, NACK

HOST = "172.17.0.2"  # The server's hostname or IP address
PORT = 65432  # The port used by the server


################

def get_md5(bytes_data):
    return hashlib.md5(bytes_data.encode('utf-8')).hexdigest() + "\n"

################

def run_client():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))


    metadata = s.recv(1024).decode()

    print(f"Metadata received {metadata}")

    file_name, file_size, checksum = metadata.split('|')
    file_size = int(file_size)

    s.sendall(ACK.encode("utf-8"))

    while True:
        file_read = 0

        data = ""

        while(file_read < file_size):
            data += s.recv(1024).decode()
            file_read += 1024


        print("File read")

        md5_data = get_md5(data)

        print(len(md5_data))
        print(checksum[-1])

        if(str(md5_data) == checksum):
            print("Checksum match writing files")
            s.sendall(ACK.encode("utf-8"))
            break;
        else:
            print("Checksum error! getting file again")
            s.sendall(NACK.encode("utf-8"))





if __name__ == "__main__":
    run_client()


