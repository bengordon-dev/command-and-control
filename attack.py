import socket

SERVER_HOST = "10.0.2.5"  # Replace with the actual IP address of 'banana'
SERVER_PORT = 5003
BUFFER_SIZE = 1024 * 128
SEPARATOR = "<sep>"

s = socket.socket()
s.connect((SERVER_HOST, SERVER_PORT))

cwd = s.recv(BUFFER_SIZE).decode()
print("[+] Current working directory:", cwd)

while True:
    command = input(f"{cwd} $> ")
    if not command.strip():
        continue
    s.send(command.encode())
    if command.lower() == "exit":
        break

    output = s.recv(BUFFER_SIZE).decode()
    results, cwd = output.split(SEPARATOR)
    print(results)

s.close()
