# echo-server.py

import socket

HOST = ""  # Standard loopback interface address (localhost)
PORT = 65432  # Port to listen on (non-privileged ports are > 1023)

def run_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen()

    conn, addr = s.accept()
    with conn:
        print(f"Connected by {addr}")
        with open("../../objects/small-0.obj", 'r') as file:
            file_data = file.read()
            bytes_data = file_data.encode('utf-8')
            print(bytes_data)
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                conn.sendall(bytes_data)


def test_file():
    with open("../../objects/small-0.obj", 'r') as file:
        file_data = file.read()
        bytes_data = file_data.encode('utf-8')
        print(bytes_data[:1024])
        print(len(bytes_data))

        c = 0
        
        while(c<=len(bytes_data)):
            print(bytes_data[c:c+1024])
            c+=1024

if __name__ == "__main__":
    #run_server()
    test_file()


