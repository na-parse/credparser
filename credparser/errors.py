'''
credparser / errors
'''

class credparserError(Exception):
    ''' Generic credparserError exception class '''
    pass

class CryptError(credparserError):
    ''' Cryptography related problems '''
    pass

class UsageError(credparserError):
    ''' Invalid credparser usage '''
    pass

class InvalidCredentialString(credparserError):
    ''' Invalid credential string / decode failure '''
    def __init__(self, msg: str = None):
        super().__init__('Invalid or corrupt credential string')

class InvalidDataType(credparserError):
    ''' Username and Password must be ascii compatible str '''
    def __init__(self):
        super().__init__('Username and password values must be ascii compatible text')
