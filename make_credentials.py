#!/usr/bin/env python3
'''
make_credentials.py

Command-line utility to generate encoded credential strings using credparser.
'''

import credparser
import getpass
import sys

def main():
   print("Credential String Generator")
   print("=" * 40)
   print()
   print("This utility generates encoded credential strings for use with credparser.")
   print("For API Keys: Use a descriptive label as username, API key as password.")
   print()
   
   try:
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
       creds = credparser.CredParser(username=username, password=password)
       
       print()
       print("Generated Credential String:")
       print("-" * 40)
       print(creds.credentials)
       print()
       
       # Verification
       print("Verification:")
       print(f"Username: {creds.username}")
       print(f"Password: {'*' * len(creds.password)}")
       
   except KeyboardInterrupt:
       print("\nOperation cancelled.")
       sys.exit(1)
   except Exception as e:
       print(f"Error: {e}")
       sys.exit(1)

if __name__ == "__main__":
   main()