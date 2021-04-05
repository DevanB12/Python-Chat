import socket                
  
HOST = '127.0.01'  # The server's hostname or IP address
PORT = 8822        # The port used by the server

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    

    while True:
        msg = input('Input: ')
        s.send(msg.encode())
        data = s.recv(1024)
        if not data:
            break
        print('Received:', data.decode('utf-8'))
       # print('Received', repr(data))
        








