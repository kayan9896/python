import socket
import os

class PeerClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Changed to SOCK_STREAM
        self.buffer_size = 1024

    def connect(self):
        self.sock.connect((self.host, self.port))  # Establish a connection with the server

    def send_data(self, data):
        data = data.encode()
        self.sock.sendall(data)  # Changed to sendall()

    def receive_data(self):
        data = self.sock.recv(self.buffer_size)
        print(data)
        return data.decode()


    def register(self, peer_name):
        self.send_data(f"REGISTER {peer_name}")
        response = self.receive_data()
        if response == "REGISTERED":
            print("Registered successfully")
        else:
            print("Registration failed")

    def list_files(self):
        self.send_data("LIST")
        response = self.receive_data()
        if response.startswith("AVAILABLE_FILES:"):
            files = response.split(":")[1].split("\n")
            print("Available Files:")
            for file in files:
                print(f" -> {file}")
        else:
            print("Failed to retrieve file list")

    def request_file(self, file_name):
        self.send_data(f"REQFILE {file_name}")
        response = self.receive_data()
        if response == "ACCEPTED":
            print("File request accepted")
            self.receive_file(file_name)
        elif response == "DENIED":
            print("File request denied")
        elif response == "FILE_NOT_FOUND":
            print("File not found")
        else:
            print("Unknown response")

    def receive_file(self, file_name):
        self.send_data(f"SENDFILE {file_name}")
        response = self.receive_data()
        if response == "FILE_ACCEPTED":
            with open(file_name, 'wb') as f:
                while True:
                    data = self.sock.recv(self.buffer_size)
                    if not data:
                        break
                    f.write(data)
            print("File received successfully")
        else:
            print("Failed to receive file")

if __name__ == "__main__":
    host = "0.0.0.0"
    port = 5000
    client = PeerClient(host, port)
    client.connect()
    # Register with the server
    client.register("peer_client")

    # List available files
    client.list_files()





import socket
import threading
import os

class Peer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.host, self.port))
        self.peer_list = {} 
        self.files = {}

    def listen(self):
        self.sock.listen(1)
        print(f"Listening on {self.host}:{self.port}")
        while True:
            client_socket, client_address = self.sock.accept()
            client_handler = threading.Thread(target=self.handle_client, args=(client_socket, client_address))
            client_handler.daemon = True
            client_handler.start()

    def handle_client(self, client, client_addr):
        print(f"New connection from {client_addr}")
        try:
            req = client.recv(1024).decode().strip()
            parts = req.split()
            if len(parts) > 1:
                        cmd, data = parts[0], parts[1]
            else:
                        cmd = parts[0]
                        data = ''  # Set data to empty string if not provided

            if cmd == 'REGISTER':  # Registering peer and its available files
                        if data:  # Check if data is not empty
                            self.peer_list[client_addr] = data.split(',')
                        else:
                            self.peer_list[client_addr] = []  # Set peer list to empty if no data provided
                        print(f"Peer {client_addr} registered with files : {self.peer_list[client_addr]}")
                        client.sendall(b"REGISTERED")  # Send REGISTERED response

            elif cmd == 'LIST': 
                print(1)
                self.send_files_list(client)

            elif cmd == 'REQFILE':  #Receiving file request
                filename = data
                if self.handle_file_request(client , filename):
                    self.send_file(client , filename)        
                else:
                    self.deny_file_req(client , filename)        

            elif cmd == 'BYE':
                print(f"Peer {client_addr} disconnected.")
                del self.peer_list[client_addr]
            client.close()
        except Exception as e:
            print(f"Error : {e}")
            client.close()

    def broadcast_registration(self, port):
        for ip in self.peer_list:            
            try:                 
                client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client_socket.connect((ip, int(port)))
                client_socket.sendall(b'REGISTER ' + str(self.files).encode())
                client_socket.close()
            except:
                print(f"Connection failed with {ip}")      

    def send_files_list(self, client):
        print(2)
        client.sendall(b'AVAILABLE_FILES:' + str(list(self.files.keys())).encode())

    def handle_file_request(self, client , filename):
        fn = filename.split('/')[-1]
        if fn in self.files:  
            return True
        else:
            return False

    def send_file(self, client, filename):
        with open(filename, 'rb') as f:
            data = f.read(1024)
            while data:
                client.sendall(data)
                data = f.read(1024)
        print(f"Sent file {filename}")

    def deny_file_req(self, client, filename):
        client.sendall(b'DENY')

    def request_file(self, ip , port , filename):
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((ip, int(port)))
            client_socket.sendall(b'REQFILE ' + filename.encode())
            data = client_socket.recv(1024).decode()
            if data == 'DENY':
                print("File request denied.")        
            else:
                f = open(filename.split('/')[-1], 'wb')
                data = client_socket.recv(1024)
                while data:
                    f.write(data)
                    data = client_socket.recv(1024)
                f.close()
                print(f"File {filename} received successfully.")      
            client_socket.close()   

        except Exception as e:
            print(f"Error occurred: {e}")


    def register_file(self, filename):
        if os.path.exists(filename):
            self.files[filename] = os.path.getsize(filename)
            print(f"File {filename} registered.")
        else:
            print(f"Error: File {filename} not found.")        

if __name__ == "__main__":
    host = '0.0.0.0'
    port = 5000
    peer = Peer(host, port)

    #Registering files in current directory
    for f in os.listdir():
        if os.path.isfile(f) and not f.startswith('.'):
            peer.register_file(f)

    #Starting server
    peer_listening_thread = threading.Thread(target=peer.listen)   
    peer_listening_thread.daemon = True
    peer_listening_thread.start()
    #Registering to other peers
    peer.broadcast_registration(port)    

    print("Enter 'exit' to stop the server: ")
    while True:
        inp = input().strip()
        if inp == 'exit':
            break
        parts = inp.split()
        if len(parts) == 3: 
            cmd, ip , port = parts               
        elif len(parts) == 2:
            cmd , filename = parts  
        if cmd == 'REQ':   # requesting file from peer
            peer.request_file(ip, port, filename)        
        elif cmd =='LIST': 
            print("Available Files : " )
            for file in peer.files:  print(file)  

    print("Shutting down server...")
    peer.sock.close()
