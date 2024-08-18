import socket
from time import sleep,time
import os
import configs
from _thread import start_new_thread
def send_file_tcp (file_addres , tcp_socket :socket.socket,file_seek=0,chunk_size=4096):
    with open (file_addres,mode="rb") as f :
        f.seek(0, 2) 
        size = f.tell() - file_seek # Get File Size
        f.seek(file_seek) 
        

        tcp_socket.send(f"!S{size}".encode())
    
        chunk_size = 4096
        bytes_sent = 0

        while bytes_sent < size:
            chunk = f.read(chunk_size)
            if not chunk:  # End of file
                break
            tcp_socket.sendall(chunk)  # Send the chunk via TCP
            bytes_sent += len(chunk)


def send_file_tcp_os_similar(file_address, tcp_socket: socket.socket, file_seek=0)->bool:
    with open(file_address, mode="rb") as f:
        f.seek(0, 2) 
        size = f.tell() - file_seek # Get File Size
        f.seek(file_seek) 
        tcp_socket.send(f"!S{size}".encode())
        sent_bytes = tcp_socket.sendfile(f)

        return sent_bytes == size
    



def recv_file_tcp(save_as, tcp_socket: socket.socket, buffer_size=4096):
    size_message = tcp_socket.recv(2048).decode('utf-8')  # Adjust buffer size if needed
    if not size_message.startswith('!S') :
        raise ValueError("Invalid size message format received")

    # Extract the file size from the message
    size = int(size_message[2:])
    bytes_received = 0

    # Open the file to save the received data
    with open(save_as, 'wb') as f:
        while bytes_received < size:
            # Receive a chunk of data from the socket
            chunk = tcp_socket.recv(min(buffer_size, size - bytes_received))
            if not chunk:
                break
            f.write(chunk)
            bytes_received += len(chunk)
    


class Divice:
    # address is ip addres and tcp port
    def __init__(self,version,address,name=None,platform=None) -> None:
        #self.name=name
        self.version=version
        self.address=address
        if name==None:
            self.name=socket.gethostbyaddr(address[0])[0]
        else:
            self.name=name
        self.platform=platform

    def update():#TODO update the information abut this Divece
        pass

    def __eq__(self, other) -> bool:
        return self.name==other.name and self.address == other.address
    def __str__(self) -> str:
        if self.name:
            return f"{self.name}-{self.version}"
        else:
            return f"{self.address[0]}-{self.version}"

    def __repr__(self) -> str:
        return self.__str__()
class Udp_Brodcast :
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.__start_lock=False
        self.is_in_progress=False


    def detect_divces(timer=6)->list:
        divces=[]
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_address = ('', configs.network.LOCAL_UDP_BRODCAST_PORT)
        sock.bind(server_address)
        target_time=time()+timer
        while time()<=target_time:
            data, address = sock.recvfrom(1024)
        
            data =data.decode()
            if "pylocalshare" in data:
                data = data.split(" ")
                d = Divice(data[data.index("from")+1],(address[0],data[data.index("on")+1]))
                if d not in divces : 
                    divces.append(d)

        return divces

    def start(self):
        def main_loop():
            try :
                while self.__start_lock:
                    self.is_in_progress = True
                    message = f"pylocalshare from {configs.network.LOCAL_UDP_BRODCAST_VERSOINS} on {configs.network.LOCAL_TCP_PORT}"
                    broadcast_address = ('<broadcast>',configs.network.LOCAL_UDP_BRODCAST_PORT)
                    
                    self.sock.sendto(message.encode(), broadcast_address)
                    sleep(5)
            finally :
                self.is_in_progress = False
        if not self.is_in_progress:
            self.__start_lock=True
            start_new_thread(main_loop,tuple([]))


    def stop(self):
        self.__start_lock = False
    
    def __del__(self) -> None:
        self.sock.close()


if __name__ == "__main__":
    udp = Udp_Brodcast()
    udp.start()
    sleep(1)
    print(Udp_Brodcast.detect_divces())
    while True :
        cmd = input(">>>")
        print(udp.is_in_progress)


        if  cmd == "y":
            udp.stop()

        if  cmd == "q":
            udp.stop()
            del udp
            break