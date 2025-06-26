'''
credparser / __init__
'''

from .errors import *
from .mutators import _encode_credentials, _decode_credentials

class CredParser():
    '''
    CredParser

    ...docstring goes here...
    The username and password values are never statically saved in the class.
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
        
        self.credentials = credentials

        if username and password:
            # Automatically generate the credential string
            self.credentials = _encode_credentials(username, password)
        
        if self.credentials:
            # Credential string verification for either auto-gen or argument
            try:
                _, _ = _decode_credentials(self.credentials)
            except InvalidCredentialString as e:
                raise InvalidCredentialString(e) from None


    @property
    def username(self) -> str:
        ''' return the username for the loaded credentials string '''
        if not self.credentials: return None
        username, _ = _decode_credentials(self.credentials)
        return username


    @property
    def password(self) -> str:
        ''' return the password for the loaded credentials string '''
        if not self.credentials: return None
        _, password = _decode_credentials(self.credentials)
        return password


    def load(self, credentials: str):
        '''
        Load a credential string into the class post-init
        '''
        self.credentials = credentials
        try:
            _, _ = _decode_credentials(credentials)
        except InvalidCredentialString as e:
            raise InvalidCredentialString(e) from None

