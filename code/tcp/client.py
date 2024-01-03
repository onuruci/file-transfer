# echo-client.py

import socket
import hashlib
import time
import select

from utils import ACK, NACK

HOST = "172.17.0.2"  # The server's hostname or IP address
PORT = 65431  # The port used by the server
DIR_NAME = "../../objects/"

################

def get_md5(bytes_data):
    return hashlib.md5(bytes_data.encode('utf-8')).hexdigest() + "\n"

################

def get_file_and_write(s, file_size, file_name, checksum):
    while True:
        file_read = 0

        data = ""

        while(file_read < file_size):
            recieved = s.recv(min(1024, file_size - file_read)).decode()
            file_read += len(recieved)

            data += recieved


        print("File read")

        md5_data = get_md5(data)

        print(md5_data)
        print(checksum)

        if(str(md5_data) == checksum):
            print("Checksum match writing files")

            with open(DIR_NAME + file_name, "w") as file:
                file.write(data)

            s.sendall(ACK.encode("utf-8"))
            break;
        else:
            print("Checksum error! getting file again")
            s.sendall(NACK.encode("utf-8"))

################

def run_client():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))

    for i in range(20):

        metadata = s.recv(1024).decode()
        print("\n\n")
        print(f"Metadata received {metadata}")

        file_name, file_size, checksum = metadata.split('|')
        file_size = int(file_size)

        s.sendall(ACK.encode("utf-8"))

        get_file_and_write(s, file_size, file_name, checksum)






if __name__ == "__main__":
    for i in range(30):
        run_client()


