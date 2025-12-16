'''
credparser / __init__
'''
__version__ = '1.1.0'

# Load and trigger configuration processing
from .config import config

# Expose credparser errors in base namespace
from .errors import *

# Main CredParser class object
from .credparser import CredParser

# Interactive credential creation guide
from .guide import make_credentials, configure_credparser
