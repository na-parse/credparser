'''
credparser / __init__
'''

from .errors import *
from .mutators import _encode_credentials, _decode_credentials
from pathlib import Path

# Setup the default master.seed file path based on user Home directory
DEFAULT_SEED_FILE = Path().home() / '.credparser/master.seed'

class CredParser():
    '''
    Credential parser for encoding/decoding username/password pairs.
    
    Handles credential string generation from username/password pairs and
    extraction of credentials from encoded strings. Supports both initialization
    with raw credentials or pre-encoded credential strings.
    
    Args:
        username (str, optional): Username for credential pair
        password (str, optional): Password for credential pair  
        credentials (str, optional): Pre-encoded credential string
        seed_path (Path, optional): Alternative master.seed file location
        
    Raises:
        UsageError: Invalid parameter combinations
        InvalidCredentialString: Malformed credential string
        
    Examples:
        >>> parser = CredParser(username='user', password='pass')
        >>> parser = CredParser(credentials='encoded_string')
        >>> parser = CredParser()  # Initialize empty
    '''
    def __init__(self,
        username: str = None,
        password: str = None,
        credentials: str = None,
        seed_path: Path = None
    ):
        # Username and password must either be both set or None
        if (
            (username is not None and password is None)
            or (username is None and password is not None)
        ):
            errmsg = 'username and password must be either set or None'
            raise UsageError(errmsg)
        
        # Credential string cannot be manually set with username and password
        if ( (username or password) and credentials ):
            errmsg = 'Cannot set username and password with a credential string'
            raise UsageError(errmsg)        
        
        self._credentials = credentials
        self.seed_path = (
            Path(seed_path) if seed_path is not None else DEFAULT_SEED_FILE
        )

        if username is not None and password is not None:
            # Automatically generate the credential string
            self._credentials = _encode_credentials(
                username=username, 
                password=password,
                seed_path=self.seed_path
            )

        if self._credentials:
            # Credential string verification for either auto-gen or argument
            try:
                _, _ = _decode_credentials(self._credentials, seed_path=self.seed_path)
            except DecodeFailure as e:
                raise DecodeFailure(e) from None
    
    def __repr__(self):
        if self._credentials is None:
            details = '<uninitialized>'
        else:
            details = (
                f'credentials=\'{self.credentials}\', '
                f'username=\'{self.username}\', '
                f'password={"*"*len(self.password)}, '
                f'seed_path={str(self.seed_path)}'
            )
        return f'CredParser({details})'
    
    def __str__(self):
        return self.__repr__()


    @property
    def credentials(self) -> str:
        '''
        Get the encoded credential string.
        
        Returns:
            str: Encoded credential string or None if uninitialized
        '''
        return self._credentials

    @property
    def username(self) -> str:
        '''
        Extract username from credential string.
        
        Returns:
            str: Decoded username or None if no credentials loaded
            
        Raises:
            DecodeFailure: Credential string cannot be decoded
        '''
        if not self.credentials: return None
        try:
            username, _ = _decode_credentials(self._credentials, seed_path=self.seed_path)
        except DecodeFailure as e:
            raise DecodeFailure(e) from None
        return username


    @property
    def password(self) -> str:
        '''
        Extract password from credential string.
        
        Returns:
            str: Decoded password or None if no credentials loaded
            
        Raises:
            DecodeFailure: Credential string cannot be decoded
        '''
        if not self.credentials: return None
        try:
            _, password = _decode_credentials(self._credentials, seed_path=self.seed_path)
        except DecodeFailure as e:
            raise DecodeFailure(e) from None
        return password


    def load(self, credentials: str):
        '''
        Load pre-encoded credential string post-initialization.
        
        Args:
            credentials (str): Encoded credential string to load
            
        Raises:
            DecodeFailure: Credential string cannot be decoded
        '''
        self._credentials = credentials
        try:
            _, _ = _decode_credentials(self._credentials, seed_path=self.seed_path)
        except DecodeFailure as e:
            raise DecodeFailure(e) from None

    def reset(self,username: str, password: str):
        '''
        Reinitialize with new username/password pair.
        
        Args:
            username (str): New username
            password (str): New password
        '''
        self.__init__(username=username,password=password, seed_path=self.seed_path)
