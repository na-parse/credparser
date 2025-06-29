'''
credparser / config.py

Configuration module handling and defining configurable elements

Default values are defined as module level attributes and are based on best
recommendations.  Deployments that desire/require deviations can create the
'.config' file in the module directory.

Config settings:
    SALT_LEN = <length_for_salt>
    MAX_HASH_ROUNDS = <Maximum number of key-gen hash rounds>
    MIN_HASH_ROUNDS = <Minimum number of key-gen hash rounds>
'''
from .errors import *
from pathlib import Path
import sys

CREDPARSER_CONFIG_FILE = Path(__file__).parent / '.config'
DEFAULT_SALT_LEN = 12
DEFAULT_MAX_HASH_ROUNDS = 24
DEFAULT_MIN_HASH_ROUNDS = 3

CONFIG_SETTINGS = [
    'salt_len',
    'max_hash_rounds',
    'min_hash_rounds'
]

class CredParserConfig:
    '''
    Configuration handler for the CredParser module
    
    Provides centralized handler for setting configuration values, default
    assignments, and config file overrides.  Intended for module-internal use.
    
    Args:
        salt_len (int, optional): Length setting for salt value
        max_hash_rounds (int, optional): Maximum number of key-gen hash rounds
        min_hash_rounds (int, optional): Minimum number of key-gen hash rounds
        config_file (Path, optional): Manually specify path for config file
        
    Raises:
        ConfigError: Invalid data in config file
 
    '''
    def __init__(self,
        salt_len: int = None,
        max_hash_rounds: int = None,
        min_hash_rounds: int = None,
        config_file: Path = None
    ):
        self.config_file = Path(config_file or CREDPARSER_CONFIG_FILE)
        settings = read_config_file(self.config_file)

        try:
            # Settings processing
            self.salt_len = int(_config_value(
                salt_len, settings.get('salt_len'), DEFAULT_SALT_LEN
            ))
            self.max_hash_rounds = int(_config_value(
                max_hash_rounds, settings.get('max_hash_rounds'), DEFAULT_MAX_HASH_ROUNDS
            ))
            self.min_hash_rounds = int(_config_value(
                min_hash_rounds, settings.get('min_hash_rounds'), DEFAULT_MIN_HASH_ROUNDS
            ))
        except ValueError as e:
            errmsg = f'Bad configuration value assignment in {self.config_file}: {e}'
            raise ConfigError(errmsg)

        # Enforce minimum standards
        errors = []
        if self.salt_len < 8:
            errors.append(f'Salt Length must be >= 8: {self.salt_len}')
        if self.min_hash_rounds < 1:
            errors.append(f'Minimum hash rounds must be >= 1: {self.min_hash_rounds}')
        if errors:
            raise ConfigError(" - ".join(errors)) from None
        
    
    def __repr__(self):
        return (
            f'CredParserConfig(salt_len={self.salt_len!r}, '
            f'max_hash_rounds={self.max_hash_rounds!r}, '
            f'min_hash_rounds={self.min_hash_rounds!r}, '
            f'config_file={str(self.config_file)!r})'
        )
    
    def __str__(self):
        return self.__repr__()


def _config_value(arg_value, config_value, default_value):
    ''' Returns the highest priority passed value '''
    if arg_value is not None:
        return arg_value
    if config_value is not None:
        return config_value
    return default_value


def read_config_file(config_file: Path) -> dict:
    '''
    Reads the specified config file and returns a dictionary of all
        key = value lines found in the config file
    '''
    if config_file is None or not Path(config_file).exists():
        # Config file doesn't exist, return an empty dict
        return {}
    
    # Parse the config for all key = value pairs
    try:
        settings = {}
        with open(config_file,'r') as f:
            lines = [ 
                line.strip() for line in f.readlines() 
                if '=' in line and not line.startswith('#')
            ]
        for line in lines:
            key, value = [ s.strip() for s in line.split('=') ]
            key = key.lower()
            value = value.strip('\'"')
            if value.isdigit(): value = int(value)
            settings[key] = value
        
        return settings

    except (OSError, PermissionError) as e:
        errmsg = f'Unable to read configuration file {self.config_file}: {e}'
        raise ConfigError(errmsg)


# Create module config object
config = CredParserConfig()