# credparser Embedded Credential Parsing

`credparser` is intended to provide a light-weight credential embedding solution for scripting environments interacting with end-point REST or other API systems, while avoiding saving credentials in plain-text format.


## Quick Start

```python
from credparser import CredParser

# Create credentials from username/password
creds = CredParser(username="admin", password="secret123")
credential_string = creds.credentials

# Load credentials from string
creds = CredParser(credentials=credential_string)
print(creds.username)  # "admin"
print(creds.password)  # "secret123"
```

## Configuration

**Important**: Change the default master seed before production use.

Edit `credparser/seed.py`:

```python
MASTER_SEED = "your-secure-master-seed-here"
```

### Advanced Configuration Options

#### External Seed File

Generate an external binary seed file:
```python
import secrets
with open('.master_seed', 'wb') as f:
    f.write(secrets.token_bytes(128))
```

Modify `credparser/seed.py` to use it:
```python
import hashlib
with open('.master_seed', 'rb') as f:
    seed_bin = f.read()
    MASTER_SEED = hashlib.sha256(seed_bin).hexdigest()
```

#### Self-Hashing Seed

Hash the seed.py file itself:
```python
import hashlib
with open(__file__, 'rb') as f:
    h = hashlib.sha256()
    for chunk in iter(lambda: f.read(8192), b''):
        h.update(chunk)
MASTER_SEED = h.hexdigest()
```

#### Production Integration

```python
import os
from your_secrets_manager import get_secret

MASTER_SEED = os.getenv('CREDPARSER_MASTER_SEED') or get_secret('credparser_seed')
```

## The Problem

Secret managers are the way to go.  The `keyring` solution exists as well.  But at the end of the day, my observation has been that for small, quick REST access scripts, everyone seems to be loading plain user/password values from text files, environment variables (which are generally populated from plain text files), or some other clunky solution.

Secret managers highly complicate lightweight scripts and establish a significant barrier to entry for initial developments, keyring only really works for interactive users, and if you're loading environment from plain text, your credentials are still out there somewhere in plain text.

## credparser's Approach

You:
- Need to load a config file
- Config file needs to contain credentials
- Agree that credentials should never be stored in plain text

`credparser`:
- Basic encryption using sha256 hash based keys
- Generates a base64 string that can be easily stored in a config file
- Easy integration into python scripts for loading and decoding

## Example

Create a credential string:

```bash
git clone https://github.com/naparse/credparser.git
cd credparser
./make_credentials.py
```

Create a credential string in code:
```python
from credparser import CredParser
mycreds = CredParser(username="username", password="password")
print(mycreds.credentials)
```

Decode a credential string in code:
```python
from credparser import CredParser
credential_string = 'abcdefgHIJkILMNO01234596pa=='
mycreds = CredParser()
mycreds.load(mycredential_string)
print(f'username={mycreds.username}, password={mycreds.password}')
```

## API Reference

### CredParser Class

#### Constructor

```python
CredParser(username=None, password=None, credentials=None)
```

- `username`, `password`: Both must be provided together or both None
- `credentials`: Pre-encoded credential string
- Cannot specify both username/password and credentials

#### Properties

- `username`: Returns decoded username (read-only)
- `password`: Returns decoded password (read-only)
- `credentials`: The encoded credential string (read-only)

#### Methods

- `load(credentials)`: Load new credential string post-initialization
- `reset(username, password)`: Reset with a new username and password value

## Error Handling

- `UsageError`: Invalid parameter combinations
- `InvalidCredentialString`: Corrupt/invalid credential data
- `InvalidDataType`: Non-ASCII string inputs
- `CryptError`: Cryptographic operation failures

## Security Notes

- Credentials are never stored as plaintext in memory
- Each credential string uses unique salt generation
- Two-level key derivation with SHA-256 hashing
- Master seed must be accessible to any user/system account needing to encode/decode
- Credential strings should be treated as sensitive information
- The salt value within credential strings provides the security layer


## Example Integration

```python
import credparser

# REST API authentication
creds = credparser.CredParser(credentials=stored_cred_string)
response = requests.get(
    api_url,
    auth=(creds.username, creds.password)
)
```