'''
credparser / mutators

Manipulators for data encoding and decoding

'''
try:
    from .seed import MASTER_SEED
except ImportError:
    raise CryptError(f'Unable to retrieve MASTER_SEED - See documentation')

from .errors import *
import hashlib
import base64
import random
import struct
from typing import Tuple

SALT_LEN = 12

def _binflip(invalue: int) -> int:
    return int('{:08b}'.format(invalue)[::-1], 2)

def _generate_salt(length: int) -> str:
    grains = (
        "0123456789"
        "abcdefghijklmnopqrstuvwxyz"
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    )
    return ''.join(random.choice(grains) for _ in range(length))


def _str_to_int(s: str) -> int:
    return int.from_bytes(s.encode('ascii'), 'big')

def _int_to_bytes(i: int) -> bytes:
    length = ( i.bit_length() + 7 ) // 8 or 1
    return i.to_bytes(length, 'big')

def _generate_key(master: str, salt: str, additional: str = None) -> bytes:
    '''
    Master key and Salt are converted to integers and multiplied together
      and converted to a sha256 hash.
    
    Additional is converted to an int (65537 if not supplied) and multiplied
      by the floor div/7 of the salt and converted to a sha256 hash.
    
    The hashes are XORed and returned as the key.
    '''
    master_int = _str_to_int(master)
    salt_int = _str_to_int(salt)

    product = master_int * salt_int

    if additional is not None:
        additional_int = _str_to_int(str(additional))
    else:
        additional_int = 65537
    
    mask = additional_int * ( salt_int // 7 )
    
    # Convert to bytes for hashing
    product_bytes = _int_to_bytes(product)
    mask_bytes = _int_to_bytes(mask)
    product_hash = hashlib.sha256(product_bytes).digest()
    mask_hash = hashlib.sha256(mask_bytes).digest()
    xored = bytes(a ^ b for a, b in zip(product_hash, mask_hash))
    return hashlib.sha256(xored).digest()


def _key_filter(data: bytes, key: bytes) -> bytes:
    extended_key = (key * ((len(data) // len(key)) + 1))[:len(data)]
    return bytes(a ^ b for a, b in zip(data, extended_key))


def _encode_credentials(username: str, password: str) -> str:
    '''
    Encode is wrapped to provide error handling and catching for data types
    '''
    if not isinstance(username, str) or not isinstance(password, str):
        raise InvalidDataType()
    try:
        return _encode(username, password)
    except Exception as e:
        raise e from None

def _encode(username: str, password: str, master: str = None) -> str:
    master = master or MASTER_SEED
    salt = _generate_salt(SALT_LEN)
    key1 = _generate_key(master, salt)

    # Prepare username section: salt + len(username) + username
    username_section = salt + chr(len(username)) + username
    username_flipped = bytes(_binflip(b) for b in username_section.encode('ascii'))
    username_encrypted = _key_filter(username_flipped, key1)
    
    key2 = _generate_key(
        master, 
        salt, 
        hashlib.sha256(username_encrypted).hexdigest()
    )
    
    # Encrypt password
    password_flipped = bytes(_binflip(b) for b in password.encode('ascii'))
    password_encrypted = _key_filter(password_flipped, key2)
    
    # Combine and encode
    cipher_text = username_encrypted + password_encrypted
    cipher_b64 = base64.b64encode(cipher_text).decode()
    
    return salt + cipher_b64



def _decode_credentials(credential_string: str) -> Tuple[str, str]:
    '''
    Actual decode method is wrapped to provide better error catching and
      handling for decryption failures.
    '''
    try:
        return _decode(credential_string)
    except UnicodeDecodeError as e:
        raise InvalidCredentialString() from None
    except ValueError as e:
        if 'Incorrect padding' in str(e):
            raise InvalidCredentialString() from None
        else:
            raise CryptError(str(e)) from None
    

def _decode(credential_string: str, master: str = None) -> Tuple[str, str]:
    master = master or MASTER_SEED
    salt = credential_string[:SALT_LEN]
    cipher_b64 = credential_string[SALT_LEN:]
    cipher_text = base64.b64decode(cipher_b64)
    key1 = _generate_key(master, salt)

    # Decrypt first 9 bytes to get salt verification and username length
    header_encrypted = cipher_text[:SALT_LEN+1]
    header_decrypted = _key_filter(header_encrypted, key1)
    header_unflipped = bytes(_binflip(b) for b in header_decrypted)

    # Verify salt
    if header_unflipped[:SALT_LEN].decode('ascii') != salt:
        raise ValueError("Invalid credential string or master key")
    
    # Get Username field length
    username_len = header_unflipped[SALT_LEN]

    # Decode the full username header section cipher text
    username_cipher = cipher_text[:SALT_LEN+1+username_len]
    username_decrypted = _key_filter(username_cipher, key1)

    # Extract the username from the username header section
    username = bytes(
        _binflip(b) for b in username_decrypted
    ).decode('ascii')[SALT_LEN+1:]
    
    # Second level key
    username_section_encrypted = cipher_text[:SALT_LEN+username_len+1]
    key2 = _generate_key(
        master, 
        salt, 
        hashlib.sha256(username_section_encrypted).hexdigest()
    )
    
    # Decrypt password
    password_offset = SALT_LEN + username_len + 1
    password_encrypted = cipher_text[password_offset:]
    password_decrypted = _key_filter(password_encrypted, key2)
    password = bytes(_binflip(b) for b in password_decrypted).decode()
    
    return username, password
