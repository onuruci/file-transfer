# echo-server.py

import socket
import os
import time

from utils import ACK, NACK

HOST = ""  # Standard loopback interface address (localhost)
PORT = 65431  # Port to listen on (non-privileged ports are > 1023)

DIR_NAME = "../../objects/"


#################

# read file and return it as bytes

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

# waits for a message from client
# if response is ACK return true
# else return false

def message_status(connection):
    status_data = connection.recv(1024).decode()

    if(status_data == ACK):
        return True

    return False

#################

# main function to send a file
# generates a metadata sends it
# wait for ACK response from client
# sends the file
# discard unreliable possibilities since built on tcp

def send_all_file(conn, filename):
    file_size = os.path.getsize(DIR_NAME + filename)

    # send metadata
    while True:
        md5_data = read_file(filename + ".md5")

        metadata = f"{filename}|{file_size}|{md5_data}"
        conn.sendall(metadata.encode('utf-8'))

        print("\n\n")
        print(metadata)

        print(f"Metadata sent for file {filename}")


        if(message_status(conn)):
            print("ACK received")
            break;

    # send file
    while True:
        print("Sending file data")
        file_data = read_file_bytes(filename)
        file_size = int(file_size)

        data_sent = 0
        data_end = 1024

        i = 1

        conn.sendall(file_data)


        if(message_status(conn)):
            print("ACK received")
            break;


#################

# main function
# waits for connection
# sends files

def run_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen()

    while True:
        conn, addr = s.accept()
        with conn:
            print(f"\nConnected by {addr}\n")

            start_time = time.time()
            # main loop for sending files
            for i in range(10):

                filename = "small-"+str(i)+".obj"
                send_all_file(conn, filename)
                filename = "large-"+str(i)+".obj"
                send_all_file(conn, filename)

            end_time = time.time()
            elapsed_time = end_time - start_time

            print(f"Elapsed time: {elapsed_time} seconds")


            conn.close()




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

