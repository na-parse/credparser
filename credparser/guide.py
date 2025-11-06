'''
credparser / guide.py

Built in CLI dialogue guide for creating a credential string
Intended to provide credential creation options via an API
'''

from .credparser import CredParser
import getpass
import sys

def make_credentials(target: str = None) -> CredParser:
    '''
    Guided interactive credential parser object creation

    Returns a CredParser object with the credential field populated. 

    '''
    print("Credential String Generator")
    print("=" * 40)
    print()
    print(
        f'Creating an encoded credential string using the credparser library.\n'
        f'For API keys: Use a descriptive label as username, API key as password.\n'
        f'\n'
    )

    try:
        if target is not None:
            print(f'Enter credentials for: {target}')
        
        # Get username
        username = input("Username/Label: ").strip()
        if not username:
            print("Error: Username cannot be empty")
            sys.exit(1)
        
        # Get password securely
        password = getpass.getpass("Password/API Key: ")
        if not password:
            print("Error: Password cannot be empty")
            sys.exit(1)
        
        # Generate credential string
        creds = CredParser(username=username, password=password)
        
        print()
        print("Generated Credential String:")
        print("-" * 40)
        print(creds.credentials)
        print()
        
        # Verification
        print("Verification:")
        print(f"Username: {creds.username}")
        print(f"Password: {'*' * len(creds.password)}")

        return creds
        
    except KeyboardInterrupt:
        print("\nOperation cancelled.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
