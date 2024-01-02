import socket
import os
import math
import time
import threading
 

localIP     = ""

localPort   = 20001

bufferSize  = 1024

DIR_NAME = "../../objects/"

 
header_length = 8
packet_data_length = 1016
default_window = 10
window_start = 0
window_end = 100

array_lock = threading.Lock()
update_sem = threading.Semaphore(1)

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
    global window_start
    global window_end
    global recv_arr
    arr_len = len(recv_arr)

    update_sem.release()
    while True:
        """
        with array_lock:
            if(window_start == window_end or window_start >= arr_len):
                return
                break
        """
        
        receive = socket_client.recvfrom(1024)

        msg = receive[0].decode('utf-8')
        [msg_type, seq] = msg.split("|")

        seq = int(seq)

        with array_lock:
            recv_arr[seq] = -1
            update_sem.release()
            if(recv_arr.count(-1)== arr_len):
                break
    
    return

# check i and j
# if equal greater than packet_count break
# recv
# update arr

# send a packet

def send_packet(socket_client, address, n):
    global packet_data_length
    global file_data

    file_start = n * packet_data_length
    packet_size = min(packet_data_length, len(file_data) - file_start)
    packet_data = file_data[file_start: file_start+packet_size]
    file_header = str(n) + "|"
    file_header = (8-len(file_header)) * "0" + file_header
    data_to_send = str(file_header+packet_data).encode('utf-8')

    socket_client.sendto(data_to_send, address)



# send packets to client

def send_client(socket_client, address):
    # while arr[window_start] == -1 , window_start++, window_end++
    # if window_start == window_end break
    # for window_start -> window_end
    # if 0 send directly write sending time
    # calculate time find difference if larger than expected send again update send time
    global window_start
    global window_end
    global recv_arr

    arr_len = len(recv_arr)


    while True:
        update_sem.acquire()
        if(window_start == window_end or window_start >= arr_len):
            break
        with array_lock:
            while(recv_arr[window_start] == -1):
                # while marked as ACKed move the window
                if(window_end < arr_len):
                    window_end += 1

                window_start += 1
                if(window_start >= arr_len):
                    break

            for i in range(window_start, window_end):
                if(recv_arr[i] == -1):
                    # if marked ACKed continue
                    continue
                elif(recv_arr[i] == 0):
                    # if not sent at all send and write send time
                    send_packet(socket_client, address, i)
                    send_time = time.time()
                    recv_arr[i] = send_time
                else:
                    # check send time if timedout send again
                    send_time = recv_arr[i]
                    curr_time = time.time()
                    time_elapsed = curr_time - send_time

            if(window_start == window_end or window_start >= arr_len):
                break

    print(f"Sender End {window_start}")
    return



# handle send file


def send_file(filename, UDPServerSocket, address):
    global file_data
    global recv_arr
    global window_start
    global window_end

    filesize = os.path.getsize(DIR_NAME + filename)
    packet_count = int(math.ceil(filesize / float(packet_data_length)))

    # read file data
    file_data = read_file(filename)

    # listener thread
    # writing thread

    window_start = 0
    window_end = min(400, packet_count)
    recv_arr = [0] * packet_count

    listener_thread = threading.Thread(target=listen_client, args=(UDPServerSocket,))
    sender_thread = threading.Thread(target=send_client, args=(UDPServerSocket, address))

    listener_thread.start()
    sender_thread.start()

    listener_thread.join()
    sender_thread.join()

    print("Threads joined")

# get filename and return metadata

def get_metadata(filename):
    filesize = os.path.getsize(DIR_NAME + filename)
    md5_data = read_file(filename+".md5").replace("\n", "")
    packet_count = int(math.ceil(filesize / float(packet_data_length)))
    metadata = (f"{filename}|{filesize}|{md5_data}|{packet_count}")

    return metadata

# concat all metadatas into one packet and send it

def send_metadata(server_socket, address):
    metadata_all = ""

    for i in range(10):
        filename = "small-"+str(i)+".obj"

        metadata = get_metadata(filename)
        metadata_all += metadata + "*"

        filename = "large-"+str(i)+".obj"

        metadata = get_metadata(filename)
        metadata_all += metadata + "*"

    metadata_all = metadata_all[0:-1].encode('utf-8')

    send_data(server_socket, metadata_all, address)


# run server

def run_server():

    UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

    UDPServerSocket.bind((localIP, localPort))


    while(True):
        bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)

        address = bytesAddressPair[1]

        clientIP  = ("Client connected with IP Address:{}".format(address))

        print(clientIP)

        send_metadata(UDPServerSocket, address)

        start_time = time.time()
        for i in range(10):
            filename = "small-"+str(i)+".obj"

            send_file(filename, UDPServerSocket, address)
            print(f"{filename} sent successfully!")

            filename = "large-"+str(i)+".obj"

            send_file(filename, UDPServerSocket, address)
            print(f"{filename} sent successfully!")
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Execution time {elapsed_time}")








if __name__ == "__main__":
    run_server()

