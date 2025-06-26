'''
credparser / seed.py

Provider for the master key seed

USAGE:
  This script must set a MASTER_SEED value at the end of import/load.
  
  MASTER_SEED should be a string, with a recommended length of at least
    16 characters, and is used to generate a hash that will be used to
    derive a unique key for each credential string.
  
  By default, this script will set a default seed that should be changed as
    part of any library integration.  It is recommended that the seed be
    integrated with a secrets system to provide further security around the
    master seed, and the code necessary can be implemented here, ensuring 
    that the result is stored in MASTER_SEED.
'''

MASTER_SEED = "This is the default seed value, please change me!!!"
