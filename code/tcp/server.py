# echo-server.py

import socket

HOST = ""  # Standard loopback interface address (localhost)
PORT = 65432  # Port to listen on (non-privileged ports are > 1023)


def read_file_bytes(filename):
    with open("../../objects/" + filename) as file:
        file_data = file.read()
        bytes_data = file_data.encode('utf-8')
        return bytes_data

def run_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen()

    conn, addr = s.accept()
    with conn:
        print(f"Connected by {addr}")
        filename = "small-0.obj"

        md5_bytes_data = read_file_bytes(filename + ".md5")
        filename_data = filename.encode('utf-8')

        #conn.send(filename_data)
        #conn.send(md5_bytes_data)

        print(f"Checksum sent for file {filename}")

        obj_bytes_data = read_file_bytes("small-0.obj")

        length_data = str(len(obj_bytes_data)).encode('utf-8')

        #conn.send(length_data)


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

if __name__ == "__main__":
    run_server()
    #test_file()


