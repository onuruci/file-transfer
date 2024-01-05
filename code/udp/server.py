import socket
import os
import math
import time
import threading
import sys
from server_file import ServerFile
 

localIP     = ""

localPort   = 20001

bufferSize  = 1024

DIR_NAME = "../../objects/"
RESULT_DIR = "./results/"
 
header_length = 7
packet_data_length = 1014
default_window = 100
timeout_limit = 0.05
result_file = ""

file_arr = []


SYS = "SYS"
LISTEN = "LISTEN"

client_state = SYS


update_sem1 = threading.Semaphore(1)
update_sem2 = threading.Semaphore(1)
update_sem3 = threading.Semaphore(1)
update_sem4 = threading.Semaphore(1)

update_sem_arr = [update_sem1, update_sem2, update_sem3, update_sem4]

array_lock = threading.Lock()

msgFromServer       = "Hello UDP Client"

bytesToSend         = str.encode(msgFromServer)

## read file

def read_file(filename):
    with open(DIR_NAME + filename) as file:
        file_data = file.read()

        return file_data



# send data for sure polling

def send_data(s, data, address):
    while(True):
        s.sendto(data, address)

        receive = s.recvfrom(bufferSize)

        msg = receive[0].decode('utf-8')

        if(msg == 'ACK'):
            break


# listen for acks

def listen_client(socket_client):
    for i in range(len(update_sem_arr)):
        update_sem_arr[i].release()
    while True:
        try:
            receive = socket_client.recvfrom(1024)

            msg = receive[0].decode('utf-8')

            if(msg.count('|') != 2):
                continue

            [msg_type, seq, file_index] = msg.split("|")

            seq = int(seq)
            file_index = int(file_index)


            with array_lock:
                file_arr[file_index].receive(seq)
                
                update_sem_arr[file_index%4].release()
                all_completed = True
                for i in range(len(file_arr)):
                    if(not file_arr[i].is_completed()):
                        all_completed = False
                        break
                if(all_completed):
                    break

        except socket.timeout:
            all_completed = True
            for j in range(len(file_arr)):
                if(not file_arr[j].is_completed()):
                    all_completed = False
                    break
            if(all_completed):
                break
            for i in range(len(update_sem_arr)):
                update_sem_arr[i].release()
    print("Resturning from listening")
    return



# send packets to client

def send_client(file_index):
    # while arr[window_start] == -1 , window_start++, window_end++
    # if window_start == window_end break
    # for window_start -> window_end
    # if 0 send directly write sending time
    # calculate time find difference if larger than expected send again update send time
    sem_index = file_index % 4
    update_sem_arr[sem_index].release()
    while True:
        update_sem_arr[sem_index].acquire()
        if(file_arr[file_index].is_completed()):
            break

        with array_lock:
            file_arr[file_index].loop_window(file_index)

            if(file_arr[file_index].is_completed()):
                break

    return



# handle send file


def send_file(start_index):
    global file_arr

    # listener thread
    # writing thread

    for i in range(5):
        send_client(start_index + 4*i)
        print(f"{file_arr[start_index + 4*i].name} sent successfully!")


# get filename and return metadata

def get_metadata(filename, file_index, server_socket, address):
    global default_window
    global packet_data_length
    global file_arr
    global timeout_limit


    filesize = os.path.getsize(DIR_NAME + filename)
    md5_data = read_file(filename+".md5").replace("\n", "")
    packet_count = int(math.ceil(filesize / float(packet_data_length)))
    metadata = (f"{filename}|{filesize}|{md5_data}|{packet_count}")
    
    file_arr += [ServerFile(filename, filesize, "", packet_count, default_window, server_socket, address, packet_data_length, timeout_limit)]


    return metadata

# concat all metadatas into one packet and send it

def send_metadata(server_socket, address):
    metadata_all = ""

    for i in range(10):
        filename = "small-"+str(i)+".obj"
        
        metadata = get_metadata(filename, 2*i, server_socket, address)
        metadata_all += metadata + "*"


        filename = "large-"+str(i)+".obj"

        metadata = get_metadata(filename, 2*i +1, server_socket, address)
        metadata_all += metadata + "*"

    metadata_all = metadata_all[0:-1].encode('utf-8')

    send_data(server_socket, metadata_all, address)

def get_all_metadata(server_socket, address):
    metadata_all = ""

    for i in range(10):
        filename = "small-"+str(i)+".obj"

        metadata = get_metadata(filename, 2*i, server_socket, address)
        metadata_all += metadata + "*"


        filename = "large-"+str(i)+".obj"

        metadata = get_metadata(filename, 2*i +1, server_socket, address)
        metadata_all += metadata + "*"

    metadata_all = metadata_all[0:-1].encode('utf-8')
    return metadata_all


# run server

def run_server():
    global file_arr
    global client_state
    global timeout_limit

    UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

    UDPServerSocket.bind((localIP, localPort))

    with open(RESULT_DIR + result_file, "w") as file:
        while(True):
            print("Sending")
            UDPServerSocket.settimeout(10)
            address = ""
            file_arr = []
            client_state = SYS
            # Establish a connection with client
            # To ensure that both sides know that each other is working
            # Three way handshake is implemented

            # Client sends conenction request
            # Server responds with the metadata
            # Which carries needed information and accepted as an ACk on client
            # Wait for an ACK and start sending files
            while True:
                # Connect message
                try:
                    bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)
                    msg = bytesAddressPair[0].decode('utf-8')
                    if(msg == "connect"):
                        # Connected getting client address
                        print("Connected")
                        UDPServerSocket.settimeout(0.05)
                        file_arr = []
                        address = bytesAddressPair[1]
                        metadata_all = get_all_metadata(UDPServerSocket, address)
                        UDPServerSocket.sendto(metadata_all, address)
                        client_state = LISTEN
                    if(msg == "ACK"):
                        print("Metadata recevied")
                        break
                except socket.timeout:
                    if(client_state == SYS):
                        print("No connection established terminating")
                        return
                    elif(client_state == LISTEN):
                        print("Sending metadata again")
                        file_arr= []
                        metadata_all = get_all_metadata(UDPServerSocket, address)
                        UDPServerSocket.sendto(metadata_all, address)

            UDPServerSocket.settimeout(timeout_limit)

            clientIP  = ("Client connected with IP Address:{}".format(address))

            print(clientIP)

            #send_metadata(UDPServerSocket, address)

            start_time = time.time()

            listener_thread = threading.Thread(target=listen_client, args=(UDPServerSocket,))
            sender_thread1 = threading.Thread(target=send_file, args=(0,))
            sender_thread2 = threading.Thread(target=send_file, args=(1,))
            sender_thread3 = threading.Thread(target=send_file, args=(2,))
            sender_thread4 = threading.Thread(target=send_file, args=(3,))

            listener_thread.start()
            sender_thread1.start()
            sender_thread2.start()
            sender_thread3.start()
            sender_thread4.start()


            listener_thread.join()
            sender_thread1.join()
            sender_thread2.join()
            sender_thread3.join()
            sender_thread4.join()


            end_time = time.time()
            elapsed_time = end_time - start_time
            file.write(str(elapsed_time)+"\n")
            print(f"Execution time {elapsed_time}")








if __name__ == "__main__":
    if(len(sys.argv) != 4):
        print("Missing arguement should run `python3 server.py <result file> <timeout_limit> <window_size>`")
        sys.exit()
    result_file = sys.argv[1]
    timeout_limit = float(sys.argv[2])
    window_size = int(sys.argv[3])
    run_server()



