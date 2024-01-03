import hashlib

class File:
    completed_count = 0

    def __init__(self, name, packet_count, size, checksum):
        self.name = name
        self.packet_count = packet_count
        self.size = size
        self.checksum = checksum
        self.data_arr = [""] * packet_count
        self.data = ""
        self.data_count = 0

    def add_data(self, data, n):
        if(self.data_arr[n] != ""):
            return False
        self.data_arr[n] = data
        self.data_count += 1

        if(self.data_count >= self.packet_count):
            for i in range(self.packet_count):
                self.data += self.data_arr[i]

            md5 = self.get_md5()
            print(md5)
            print(self.checksum)
            File.completed_count += 1
            return True
        
        return False
    
    def log_checksum(self,):
        print(self.checksum)

    def get_md5(self,):
        return hashlib.md5(self.data.encode('utf-8')).hexdigest()


    def clean_data(self,):
        self.data = ""
        self.data_arr = []

    def print(self,):
        print(f"File {self.name}, {self.checksum}, {self.packet_count}")



