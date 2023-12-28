# echo-server.py

import socket
import os

from utils import ACK, NACK

HOST = ""  # Standard loopback interface address (localhost)
PORT = 65432  # Port to listen on (non-privileged ports are > 1023)

DIR_NAME = "../../objects/"


#################

def read_file_bytes(filename):
    with open(DIR_NAME + filename) as file:
        file_data = file.read()
        bytes_data = file_data.encode('utf-8')
        return bytes_data

#################

def read_file(filename):
    with open(DIR_NAME + filename) as file:
        file_data = file.read()

        return file_data

#################

def message_status(connection):
    status_data = connection.recv(1024).decode()

    if(status_data == ACK):
        return True

    return False


#################

def run_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen()

    conn, addr = s.accept()
    with conn:
        print(f"\nConnected by {addr}\n")
        

        while True:
            filename = "small-0.obj"

            md5_data = read_file(filename + ".md5")

            file_size = os.path.getsize(DIR_NAME + filename)

            metadata = f"{filename}|{file_size}|{md5_data}"
            conn.sendall(metadata.encode('utf-8'))

            print(f"Metadata sent for file {filename}")


            if(message_status(conn)):
                print("ACK received")
                break;

#################

def test_file():
    bytes_data = read_file_bytes("small-0.obj.md5")
    print(len(bytes_data))


    with open("../../objects/small-0.obj", 'r') as file:
        file_data = file.read()
        bytes_data = file_data.encode('utf-8')
        #print(len(bytes_data))

        c = 0
        
        while(c<=len(bytes_data)):
            #print(bytes_data[c:c+1024])
            c+=1024

#################

if __name__ == "__main__":
    run_server()
    #test_file()


