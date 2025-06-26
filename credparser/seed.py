'''
credparser / seed.py

Provider for the master key seed
'''
MASTER_SEED = "This is the default seed value, please change me!!!"

'''
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
  
  The MASTER_SEED _MUST_ remain consistent across executions, otherwise
    previously generated credentials will fail to decode.

Other examples of how to generate/maintain a MASTER_SEED:

# Master Seed file 

Use `secrets` or another method to generate an external file to use as a master seed and read here:

```python
# Create a master_seed file
import secrets
with open('.master_seed','wb') as f:
  f.write(secrets.token_bytes(128))
```

Modify credparser/seed.py to read this file:
```python
import hashlib
with open('.master_seed','rb') as f:
  seed_bin = f.read()
  # Seed must be set as a string (for now, updates roadmapped)
  MASTER_SEED = hashlib.sha256(seed_bin).hexdigest()
```

# Hash the seed.py file itself and modify with comment/filler text

Take advantage of the seed.py file itself by modifying this file and hashing it directly.

```python
import hashlib
with open(__file__,'rb') as f:
  h = hashlib.sha256
  for chunk in iter(lambda: f.read(8192),b''):
    h.update(chunk)
MASTER_SEED = h.hexdigest()
```

Reminder - Ultimately for the package to be usable, the MASTER_SEED will need to be
  visible or accessible by any user/system account that needs to be able to encode
  and decode credentials, and thus is it not a secure system.

The credential string's SALT value is the 'private' part of the equation and as such
  credential strings should still be treated as sensitive information and protected
  with appropriate filesystem security standards.

'''