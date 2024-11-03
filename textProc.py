import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import os

# Constants
VIGENERE_KEY = "Ahdzkr"
RC4_KEY = "KanangHerdaya"
AES_KEY = "Josuawarwukakaka"

def caesar_encrypt(plain, key):
    cipher = ""
    for c in plain:
        if c.isalpha():
            base = 'A' if c.isupper() else 'a'
            cipher += chr((ord(c) - ord(base) + key) % 26 + ord(base))
        else:
            cipher += c
    return cipher

def caesar_decrypt(cipher: str, key: int) -> str:
    return caesar_encrypt(cipher, 26 - (key % 26))

def vigenere_encrypt(plain: str, key: str) -> str:
    if not plain or not key:
        return ""
    
    cipher = ""
    upper_key = key.upper()
    key_length = len(upper_key)
    key_index = 0

    for c in plain:
        if c.isalpha():
            base = 'A' if c.isupper() else 'a'
            shift = ord(upper_key[key_index]) - ord('A')
            cipher += chr((ord(c) - ord(base) + shift) % 26 + ord(base))
            key_index = (key_index + 1) % key_length
        else:
            cipher += c
    return cipher

def vigenere_decrypt(cipher: str, key: str) -> str:
    if not cipher or not key:
        return ""
    
    plain = ""
    upper_key = key.upper()
    key_length = len(upper_key)
    key_index = 0

    for c in cipher:
        if c.isalpha():
            base = 'A' if c.isupper() else 'a'
            shift = ord(upper_key[key_index]) - ord('A')
            plain += chr((ord(c) - ord(base) - shift + 26) % 26 + ord(base))
            key_index = (key_index + 1) % key_length
        else:
            plain += c
    return plain

def rc4_ksa(key: str) -> list:
    S = list(range(256))
    j = 0
    for i in range(256):
        j = (j + S[i] + ord(key[i % len(key)])) % 256
        S[i], S[j] = S[j], S[i]
    return S

def rc4_prga(S: list, plaintext: str) -> str:
    i = j = 0
    result = ""
    
    for c in plaintext:
        i = (i + 1) % 256
        j = (j + S[i]) % 256
        S[i], S[j] = S[j], S[i]
        keystream_byte = S[(S[i] + S[j]) % 256]
        result += chr(ord(c) ^ keystream_byte)
    
    return result

def rc4_encrypt(plain: str, key: str) -> str:
    S = rc4_ksa(key)
    encrypted = rc4_prga(S, plain)
    return base64.b64encode(encrypted.encode()).decode()

def rc4_decrypt(cipher: str, key: str) -> str:
    S = rc4_ksa(key)
    decoded = base64.b64decode(cipher).decode()
    return rc4_prga(S, decoded)

def block_ecb_encrypt(plain: str, key: str) -> str:
    key_bytes = key.encode('utf-8')[:32].ljust(32, b'\0')
    cipher = Cipher(algorithms.AES(key_bytes), modes.ECB())
    encryptor = cipher.encryptor()
    
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(plain.encode()) + padder.finalize()
    
    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
    return base64.b64encode(encrypted_data).decode()

def block_ecb_decrypt(cipher: str, key: str) -> str:
    key_bytes = key.encode('utf-8')[:32].ljust(32, b'\0')
    cipher_obj = Cipher(algorithms.AES(key_bytes), modes.ECB())
    decryptor = cipher_obj.decryptor()
    
    encrypted_data = base64.b64decode(cipher)
    decrypted_padded = decryptor.update(encrypted_data) + decryptor.finalize()
    
    unpadder = padding.PKCS7(128).unpadder()
    data = unpadder.update(decrypted_padded) + unpadder.finalize()
    return data.decode()

def super_encrypt(plaintext: str, key: int) -> str:
    step1 = caesar_encrypt(plaintext, key)
    step2 = vigenere_encrypt(step1, VIGENERE_KEY)
    step3 = rc4_encrypt(step2, RC4_KEY)
    return block_ecb_encrypt(step3, AES_KEY)

def super_decrypt(ciphertext: str, key: int) -> str:
    step1 = block_ecb_decrypt(ciphertext, AES_KEY)
    step2 = rc4_decrypt(step1, RC4_KEY)
    step3 = vigenere_decrypt(step2, VIGENERE_KEY)
    return caesar_decrypt(step3, key)