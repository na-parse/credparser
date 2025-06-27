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
        ''' return the credential string for the current constructor '''
        return self._credentials

    @property
    def username(self) -> str:
        ''' return the username for the loaded credentials string '''
        if not self.credentials: return None
        try:
            username, _ = _decode_credentials(self._credentials)
        except InvalidCredentialString as e:
            raise InvalidCredentialString(e) from None
        return username


    @property
    def password(self) -> str:
        ''' return the password for the loaded credentials string '''
        if not self.credentials: return None
        try:
            _, password = _decode_credentials(self._credentials)
        except InvalidCredentialString as e:
            raise InvalidCredentialString(e) from None
        return password


    def load(self, credentials: str):
        '''
        Load a credential string into the class post-init
        '''
        self._credentials = credentials
        try:
            _, _ = _decode_credentials(self._credentials)
        except InvalidCredentialString as e:
            raise InvalidCredentialString(e) from None

    def reset(self,username: str, password: str):
        '''
        Reinitialize the object with a new username and password
        '''
        self.__init__(username=username,password=password)
