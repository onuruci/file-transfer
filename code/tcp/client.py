# echo-client.py

import socket

HOST = "172.17.0.2"  # The server's hostname or IP address
PORT = 65432  # The port used by the server


def run_client():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))

    while True:
        data = s.recv(1024)

        if not data:
            break

        else:
            print("Data received")

    #file_name = s.recv(1024).decode()

    #print(f"Received file name {file_name}")

    #checksum_data = s.recv(1024)

    #print("Received checksum")

    #data_length = s.recv(1024)

    #print("Receive data length")




if __name__ == "__main__":
    run_client()


