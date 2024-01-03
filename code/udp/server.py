import socket
import os
import math
import time
import threading
from server_file import ServerFile
 

localIP     = ""

localPort   = 20001

bufferSize  = 1024

DIR_NAME = "../../objects/"

 
header_length = 7
packet_data_length = 1014
default_window = 300
window_start = 0
window_end = 100
timeout_limit = 0.1

file_arr = []

update_sem1 = threading.Semaphore(1)
update_sem2 = threading.Semaphore(1)
update_sem3 = threading.Semaphore(1)
update_sem4 = threading.Semaphore(1)

update_sem_arr = [update_sem1, update_sem2, update_sem3, update_sem4]

array_lock = threading.Lock()

file_data = ""
recv_arr = []

msgFromServer       = "Hello UDP Client"

bytesToSend         = str.encode(msgFromServer)

received_acks = [0] * default_window

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
            for i in range(len(file_arr)):
                if(not file_arr[i].is_completed()):
                    all_completed = False
                    break
            if(all_completed):
                break
            for i in range(len(update_sem_arr)):
                update_sem_arr[i].release()
    return



# send packets to client

def send_client(file_index):
    # while arr[window_start] == -1 , window_start++, window_end++
    # if window_start == window_end break
    # for window_start -> window_end
    # if 0 send directly write sending time
    # calculate time find difference if larger than expected send again update send time
    print(f"Sending {file_index}")
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

    print(f"Sender End {window_start}")
    return



# handle send file


def send_file(start_index):
    global file_arr

    # listener thread
    # writing thread

    for i in range(5):
        send_client(start_index + 4*i)
        print(f"{file_arr[start_index + 4*i].name} sent successfully!")

    print("Send file ended")

# get filename and return metadata

def get_metadata(filename, file_index, server_socket, address):
    global default_window
    global packet_data_length
    global file_arr


    filesize = os.path.getsize(DIR_NAME + filename)
    md5_data = read_file(filename+".md5").replace("\n", "")
    packet_count = int(math.ceil(filesize / float(packet_data_length)))
    metadata = (f"{filename}|{filesize}|{md5_data}|{packet_count}")

    file_arr += [ServerFile(filename, filesize, "", packet_count, default_window, server_socket, address, packet_data_length)]


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


# run server

def run_server():

    UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

    UDPServerSocket.bind((localIP, localPort))

    while(True):
        bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)
        UDPServerSocket.settimeout(0.0005)

        address = bytesAddressPair[1]

        clientIP  = ("Client connected with IP Address:{}".format(address))

        print(clientIP)

        send_metadata(UDPServerSocket, address)

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
        print(f"Execution time {elapsed_time}")








if __name__ == "__main__":
    run_server()



