#!/usr/bin/env python3
'''
make_credentials.py

Command-line utility to generate encoded credential strings using credparser.
'''

from credparser import configure_credparser


if __name__ == "__main__":
   configure_credparser()