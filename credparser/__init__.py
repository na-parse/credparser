'''
credparser / __init__
'''

from .errors import *
from .mutators import _encode_credentials, _decode_credentials

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
        credentials: str = None
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

        if username is not None and password is not None:
            # Automatically generate the credential string
            self._credentials = _encode_credentials(username, password)
        
        if self._credentials:
            # Credential string verification for either auto-gen or argument
            try:
                _, _ = _decode_credentials(self._credentials)
            except InvalidCredentialString as e:
                raise InvalidCredentialString(e) from None

    def __repr__(self):
        if self._credentials is None:
            details = '<uninitialized>'
        else:
            details = (
                f'credentials=\'{self.credentials}\', '
                f'username=\'{self.username}\', '
                f'password={"*"*len(self.password)}'
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
            InvalidCredentialString: Credential string cannot be decoded
        '''
        if not self.credentials: return None
        try:
            username, _ = _decode_credentials(self._credentials)
        except InvalidCredentialString as e:
            raise InvalidCredentialString(e) from None
        return username


    @property
    def password(self) -> str:
        '''
        Extract password from credential string.
        
        Returns:
            str: Decoded password or None if no credentials loaded
            
        Raises:
            InvalidCredentialString: Credential string cannot be decoded
        '''
        if not self.credentials: return None
        try:
            _, password = _decode_credentials(self._credentials)
        except InvalidCredentialString as e:
            raise InvalidCredentialString(e) from None
        return password


    def load(self, credentials: str):
        '''
        Load pre-encoded credential string post-initialization.
        
        Args:
            credentials (str): Encoded credential string to load
            
        Raises:
            InvalidCredentialString: Credential string cannot be decoded
        '''
        self._credentials = credentials
        try:
            _, _ = _decode_credentials(self._credentials)
        except InvalidCredentialString as e:
            raise InvalidCredentialString(e) from None

    def reset(self,username: str, password: str):
        '''
        Reinitialize with new username/password pair.
        
        Args:
            username (str): New username
            password (str): New password
        '''
        self.__init__(username=username,password=password)
