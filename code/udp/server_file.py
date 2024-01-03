import time
DIR_NAME = "../../objects/"
header_length = 7
timeout_limit = 0.04

class ServerFile:
    
    def __init__(self, name, size, file_data, packet_count, default_window, socket_server, client_address, packet_data_length):
        self.name = name
        self.size = size
        self.file_data = file_data
        self.packet_count = packet_count
        self.window_start = 0
        self.window_end = min(default_window, packet_count)
        self.recv_arr = [0] * packet_count
        self.socket_server = socket_server
        self.client_address = client_address
        self.packet_data_length = packet_data_length
        self.recv_count = 0

        self.read_file()


    def receive(self, seq):
        #:print(seq)
        #print(len(self.recv_arr))
        self.recv_arr[seq] = -1
        self.recv_count += 1

    def received(self,):
        if(self.recv_count >= self.packet_count):
            return True
        return False

    def read_file(self,):
        with open(DIR_NAME + self.name) as file:
            self.file_data = file.read()

    def is_completed(self,):
        if(self.window_start == self.window_end or self.window_start >= self.packet_count):
            return True
        return False


    def send_packet(self, n, file_index):

        file_start = n * self.packet_data_length
        packet_size = min(self.packet_data_length, len(self.file_data) - file_start)
        packet_data = self.file_data[file_start: file_start+packet_size]
        file_header = str(n) + "|"
        file_header = (header_length-len(file_header)) * "0" + file_header
        file_index_header = str(file_index) + "|"
        if(file_index < 10):
            file_index_header = "0" + str(file_index) + "|"
        data_to_send = str(file_index_header+file_header+packet_data).encode('utf-8')

        self.socket_server.sendto(data_to_send, self.client_address)


    def loop_window(self, file_index):
        while(self.recv_arr[self.window_start] == -1):
            # while marked as ACKed move the window
            if(self.window_end < self.packet_count):
                self.window_end += 1

            self.window_start += 1
            if(self.window_start >= self.packet_count):
                break

        for i in range(self.window_start, self.window_end):
            if(self.recv_arr[i] == -1):
                # if marked ACKed continue
                continue
            elif(self.recv_arr[i] == 0):
                # if not sent at all send and write send time
                
                self.send_packet(i, file_index)
                
                send_time = time.time()
                self.recv_arr[i] = send_time
            else:
                # check send time if timedout send again
                send_time = self.recv_arr[i]
                curr_time = time.time()
                time_elapsed = curr_time - send_time
                if(time_elapsed >= timeout_limit):
                    self.send_packet(i, file_index)
                    self.recv_arr[i] = curr_time





