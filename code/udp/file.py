import hashlib

class File:

    def __init__(self, name, packet_count, size, checksum):
        self.name = name
        self.packet_count = packet_count
        self.size = size
        self.checksum = checksum
        self.data_arr = [""] * packet_count
        self.data = ""
        self.data_count = 0

    def add_data(self, data, n):
        self.data_arr[n] = data
        self.data_count += 1

        if(self.data_count >= self.packet_count):
            return true
        
        return false
    
    def log_checksum(self,):
        print(self.checksum)


    def clean_data(self,):
        self.data = ""
        self.data_arr = []



