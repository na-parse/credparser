'''
credparser / __init__
'''
# Load and trigger configuration processing
from .config import config

# Expose credparser errors in base namespace
from .errors import *

# Main CredParser class object
from .credparser import CredParser

# Interactive credential creation guide
from .guide import make_credentials
