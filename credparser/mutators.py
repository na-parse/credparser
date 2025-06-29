'''
credparser / mutators

Manipulators for data encoding and decoding

'''
from .seed import MasterSeed
from .errors import *
import getpass
import hashlib
import base64
import secrets
from typing import Tuple
from pathlib import Path

SALT_LEN = 12
MAX_HASH_ROUNDS = 24
MIN_HASH_ROUNDS = 3

def binflip(invalue: int) -> int:
    ''' Reverse the bit order inside a byte '''
    return int('{:08b}'.format(invalue)[::-1], 2)

def nacl(length: int) -> str:
    ''' Salt generation / Using conf friendly characters '''
    grains = (
        "0123456789"
        "abcdefghijklmnopqrstuvwxyz"
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    )
    return ''.join(secrets.choice(grains) for _ in range(length))


def generate_key(master_seed: bytes, salt: str, signer: str) -> bytes:
    ''' 
    Generate a unique key using the master seed, salt, and signer.

    In general, we are expecting to use the OS level user as the 'signer'

    Key generation workflow:
      TRANSFORM: master seed is XORed with repeating salt/signer pattern
      HASH ROUNDS: salt determines a set number of hash rounds for key
    '''
    salt_bytes = str(salt).encode('ascii')
    signer_bytes = str(signer).encode('ascii')
    
    # Transform: XOR master_seed with repeated salt+username pattern
    pattern = (
        (salt_bytes + signer_bytes) * 
        ( (len(master_seed) // len(salt_bytes + signer_bytes)) + 1 )
    )
    # Clip pattern to length of master_seed and XOR
    pattern = pattern[:len(master_seed)]
    transformed = bytes(a ^ b for a, b in zip(master_seed, pattern))
    
    # Determine hash rounds from salt
    salt_int = sum(ord(c) for c in salt)
    hash_rounds = (
        (salt_int % MAX_HASH_ROUNDS) 
        if (salt_int % MAX_HASH_ROUNDS) > MIN_HASH_ROUNDS
        else MIN_HASH_ROUNDS
    )
    
    # Multiple hash rounds for additional transformation
    result = transformed
    for _ in range(hash_rounds):
        result = hashlib.sha512(result + salt_bytes + signer_bytes).digest()
    
    return result


def key_filter(data: bytes, key: bytes) -> bytes:
    ''' XOR the data against the key '''
    extended_key = (key * ((len(data) // len(key)) + 1))[:len(data)]
    return bytes(a ^ b for a, b in zip(data, extended_key))


def _encode_credentials(username: str, password: str, seed_path: Path = None) -> str:
    '''
    Encode is wrapped to provide error handling and catching for data types
    '''
    master_seed = MasterSeed(allow_init=True, seed_path=seed_path)

    if not isinstance(username, str) or not isinstance(password, str):
        raise InvalidDataType()

    # Catch all Exceptions during encode so we can provide a reliable
    #   exception for importers when this fails: EncodeFailure()    
    try:
        return encode(master_seed.seed, username, password)
    except Exception as e:
        errmsg = (
            f'Unexpected issue while encoding credentials: {e}'
        )
        raise EncodeFailure(errmsg) from None


def encode(master_seed: bytes, username: str, password: str) -> str:
    # Keys are 'signed' by the current OS level user
    os_username = getpass.getuser()
    salt = nacl(SALT_LEN)
    key = generate_key(master_seed, salt, os_username)
    message = salt + chr(len(username)) + username + password
    egassem = bytes(binflip(b) for b in message.encode('ascii'))
    egassem_cipher = key_filter(egassem, key)
    
    cipher_b64 = base64.b64encode(egassem_cipher).decode()
    return salt + cipher_b64


def _decode_credentials(credential_string: str, seed_path: Path = None) -> Tuple[str, str]:
    '''
    Actual decode method is wrapped to provide better error catching and
      handling for decryption failures.
    '''
    master_seed = MasterSeed(allow_init=False, seed_path=seed_path)
    try:
        return decode(master_seed.seed, credential_string)
    except DecodeFailure as e:
        raise DecodeFailure(e) from None
    except Exception as e:
        # Obscure package internals and ensure importers receive a 
        # predictable exception when decode fails: DecodeFailure()
        errmsg = (
            f'Unable to decode the supplied credential string, '
            f'string, master_seed, or incorrect signer. \n--\n{e}'
        )
        raise DecodeFailure(errmsg)
    

def decode(master_seed: bytes, credential_string: str) -> Tuple[str, str]:
    # Extract plain-text Salt and base64 cipher text from credential string
    salt = credential_string[:SALT_LEN]
    cipher_b64 = credential_string[SALT_LEN:]
    cipher_text = base64.b64decode(cipher_b64)
    # Keys are 'signed' by the current OS level user
    os_username = getpass.getuser()
    key = generate_key(master_seed, salt, os_username)

    # Attempt to decrypt the cipher text
    egassem = key_filter(cipher_text, key)
    message = bytes(binflip(b) for b in egassem)

    # Data Extraction try/except block
    # - Decryption failures manifest during byte->str decodes() as the raw
    #   byte codes will not align with real ascii byte values
    try:
        # Extract message components
        msg_salt = message[:SALT_LEN].decode('ascii')
        if salt != msg_salt:
            raise DecodeFailure(
                f'Invalid credential string, unable to decode'
            )
        username_len = message[SALT_LEN]
        username = message[SALT_LEN+1:SALT_LEN+1+username_len].decode('ascii')
        password = message[SALT_LEN+1+username_len:].decode('ascii')
    except UnicodeDecodeError:
        errmsg = (
            f'Invalid credential string, unable to decode'
        )
        raise DecodeFailure(errmsg)
    
    return username, password
