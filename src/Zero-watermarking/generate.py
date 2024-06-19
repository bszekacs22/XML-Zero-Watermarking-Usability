import lxml.etree as ET
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
import os
import utils
import dfd

def pad_message(message):
    padder = padding.PKCS7(128).padder()
    padded_message = padder.update(message) + padder.finalize()
    return padded_message

def unpad_message(padded_message):
    unpadder = padding.PKCS7(128).unpadder()
    message = unpadder.update(padded_message) + unpadder.finalize()
    return message

def generate_key():
    return os.urandom(32)  # AES-256 key

def generate_iv():
    return os.urandom(16)  # AES block size

def encrypt_message(message, key, iv):
    backend = default_backend()
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=backend)
    encryptor = cipher.encryptor()
    padded_message = pad_message(message)
    encrypted_message = encryptor.update(padded_message) + encryptor.finalize()
    return encrypted_message

def decrypt_message(encrypted_message, key, iv):
    backend = default_backend()
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=backend)
    decryptor = cipher.decryptor()
    padded_message = decryptor.update(encrypted_message) + decryptor.finalize()
    message = unpad_message(padded_message)
    return message


def get_binary(FDs):
    fd_strings = []
    for fd in sorted(FDs):
        lhs, rhs = fd
        lhs_str = ''.join(sorted(lhs))
        rhs_str = ''.join(sorted(rhs))
        fd_strings.append(f"{lhs_str}->{rhs_str}")

    binary_string = ';'.join(sorted(fd_strings)) + ';'
    binary_representation = ''.join(format(ord(c), '08b') for c in binary_string)
    return binary_representation

def generate_watermark(xml_file, secret_key, iv):
    # Parse the XML file
    parser = ET.XMLParser(load_dtd=True, dtd_validation=True)
    tree = ET.parse(xml_file, parser)
    root = tree.getroot()

    # Discover FDs using the discoverFD function
    _, FDs = dfd.discover_fd(root, 'inproceedings')
    print(f"Discovered FDs: {FDs}")

    # Generate the binary string from FDs
    binary_string = get_binary(FDs)

    # Convert binary string to bytes
    binary_bytes = int(binary_string, 2).to_bytes((len(binary_string) + 7) // 8, byteorder='big')

    # Encrypt the binary data with the secret key and IV
    encrypted_watermark = encrypt_message(binary_bytes, secret_key, iv)

    return FDs



def compare(WMo, WMm):
    """
    Compare the original watermark (WMo) and the extracted watermark (WMm).

    Args:
        WMo (str): The original Zero-Watermark bits.
        WMm (str): The Zero-Watermark bits extracted from XML document.

    Returns:
        float: The similarity measure between the two watermarks.
    """
    # Step 1: Initialize common_bits
    common_bits = 0

    # Step 2-6: Compare each bit in WMo and WMm
    for i in range(len(WMo)):
        if i < len(WMm) and WMo[i] == WMm[i]:
            common_bits += 1

    # Step 7: Calculate similarity
    similarity = common_bits / len(WMo)

    # Step 8: Return similarity
    return similarity

def detect_watermark(xml_file, secret_key, iv, original_watermark):
    # Extract the binary string from the potentially tampered XML document
    extracted_binary_string = generate_watermark(xml_file, secret_key, iv)
    #print(f"Extracted Binary String: {extracted_binary_string}")

    # Convert binary string to bytes
    #extracted_binary_bytes = int(extracted_binary_string, 2).to_bytes((len(extracted_binary_string) + 7) // 8, byteorder='big')

    # Decrypt the original watermark
    #decrypted_original_watermark_bytes = decrypt_message(original_watermark, secret_key, iv)
    #decrypted_original_watermark = ''.join(format(byte, '08b') for byte in decrypted_original_watermark_bytes)
    #print(f"Decrypted Original Watermark: {decrypted_original_watermark}")

    # Compare the original and extracted binary strings
    #similarity = compare(original_watermark, extracted_binary_string)
    similarity = len(original_watermark & extracted_binary_string) / len(original_watermark | extracted_binary_string)

    # Determine if the similarity meets the threshold
    threshold = 0.9  # Define a threshold for watermark similarity
    is_valid = similarity >= threshold
    return similarity

# # Example usage
# xml_file = '../../data/mondial.xml'
#
# # Generate a secret key and IV (store these securely)
# secret_key = generate_key()
# iv = generate_iv()
# print(f"Secret Key: {secret_key}")
# print(f"IV: {iv}")
#
# # Generate the watermark
# watermark = generate_watermark(xml_file, secret_key, iv)
# print(f"Generated Watermark: {watermark}")
#
# second_watermark = generate_watermark(xml_file, secret_key, iv)
#
# print(second_watermark == watermark)