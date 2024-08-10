import socket
from time import sleep
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
    
    