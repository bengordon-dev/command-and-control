import sys
import socket
import hashlib  # Import the hashlib library

# Check if the password argument is provided
if len(sys.argv) != 2:
    print("Usage: python3 apple.py <password>")
    sys.exit(1)

# Get the password from the command line argument
PASSWORD = sys.argv[1]

# Create a function to hash the password
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Hash the password
hashed_password = hash_password(PASSWORD)

SERVER_HOST = "10.0.2.5"  # Replace with the actual IP address of 'banana'
SERVER_PORT = 5003
BUFFER_SIZE = 1024 * 128
SEPARATOR = "<sep>"

s = socket.socket()
s.connect((SERVER_HOST, SERVER_PORT))

# Send the hashed password to the server for verification
s.send(hashed_password.encode())

# Receive the authentication result from the server
auth_result = s.recv(BUFFER_SIZE).decode()

if auth_result == "Authentication successful":
    print("Password accepted. You are connected.")
else:
    print("Password incorrect. Connection denied.")
    s.close()
    sys.exit(1)

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
