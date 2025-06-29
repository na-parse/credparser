# credparser Embedded Credential Parsing

`credparser` provides a light-weight credential embedding solution for scripting environments interacting with end-point REST or other API systems, while avoiding saving credentials in plain-text format in situations where enterprise level secret management systems are not available, or integration creates an exceptional increase in complexity.

## Warning - Obfuscation, not Security

This package provides credential obfuscation and is only suggested in the following scenarios:

- Small automation scripts with no existing secrets system
- Isolated management systems with strict access rules
- Service accounts or other restricted credential types

Encoded credentials should only have the minimum necessary access to perform the required work to limit impact if they are exposed.  You are _highly_ discouraged from using `credparser` to encode administrator or personal priviledged account credentials.

## Installation

Manually place the `repo:./credparser/credparser` directory in the system/user PYTHONPATH as designed.  Package/pip support is not planned for the time being.

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

The `credparser` package uses a user-specific `master.seed` file to server as the primary seed for key generation.  

By default, the key file will be created as `$HOME/.credparser/master.seed` the first time a credential string is created.  

If the `master.seed` file changes or is moved, any existing credential strings will fail to decode.  The `master.seed` file should be protected as read-only by the user, similar to SSH keys (`chmod 600 master.seed`).  

Credential strings are also signed by the OS-level username.  The `master.seed` file can be moved to other systems, but the OS-level username must remain the same for decoding to succeed.


## Usage Examples

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

### Advanced Options

An alternative `master.seed` file/location can be specified during CredParser() initialization

```python
custom_creds = CredParser(
    username = "admin",
    password = "secret123",
    seed_path=f'/opt/secrets/{getpass.getuser()}/master.seed'
)
secret = custom_creds.credentials

# Trying to load with default master.seed path will raise DecodeFailure
creds = CredParser(credentials=secret)
```
```
credparser.errors.DecodeFailure: Invalid credential string, unable to decode
```
## Configuration

Some internal values can be adjusted by creating the file `.config` in the `credparser` module directory.

```
# Length of the salt values - Must be >= 8 (Default: 12)
SALT_LEN = 12

# Maximum number of hash rounds during key generation (Default: 24)
MAX_HASH_ROUNDS = 24

# Minimum number of hash rounds during key generation - Must be > 1 (Default: 3)
MIN_HASH_ROUNDS = 3
``` 

Note that changes to these values will invalidate previously encoded credentials for all system users.  It is recommended these settings only be modified during initial deployment.


## API Reference

### CredParser Class

#### Constructor

```python
CredParser(
    username: str = None,
    password: str = None, 
    credentials: str = None,
    seed_path: str = None
)
```

- `username`, `password`: Both must be provided together or both None
- `credentials`: Pre-encoded credential string
  - Cannot specify username/password and credentials at the same time
- `seed_path`: Override the default path to the `master.seed` file


#### Properties

- `username`: Returns decoded username (read-only)
- `password`: Returns decoded password (read-only)
- `credentials`: The encoded credential string (read-only)

#### Methods

- `load(credentials)`: Load new credential string post-initialization
- `reset(username, password)`: Reset with a new username and password value

## Error Handling

- `UsageError`: Invalid parameter combinations
- `DecodeFailure`: Corrupt credential string, invalid master-key, or incorrect signing user
- `EncodeFailure`: Internal encoding failure
- `InvalidDataType`: Non-ASCII string inputs

## Security Notes

- Credentials are never stored as plaintext in memory
- Each credential string uses unique salt generation
- Key derivation is based on multi-round/multi-element SHA512 hashing
- Credential strings are tied to combination of `master.seed` and OS-level user
- Credential strings should be treated as sensitive information


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