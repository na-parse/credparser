# credparser Embedded Credential Parsing

`credparser` provides a light-weight credential embedding solution for scripting environments interacting with end-point REST or other API systems, while avoiding saving credentials in plain-text format in situations where enterprise level secret management systems are not available, or integration creates an exceptional increase in complexity.

## Warning - Obfuscation, not Security

This package provides credential obfuscation and is only suggested in the following scenarios:

- Small automation scripts with no existing secrets system
- Isolated management systems with strict access rules
- Service accounts or other restricted credential types

Encoded credentials should only have the minimum necessary access to perform the required work to limit impact if they are exposed.  You are _highly_ discouraged from using `credparser` to encode administrator or personal privileged account credentials.

## Installation

Install from source:

```bash
pip install .
```

Or install in development mode:

```bash
pip install -e .
```

Or install directly from GitHub:

```bash
pip install git+https://github.com/naparse/credparser.git
```

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

The `credparser` package uses a user-specific `master.seed` file to serve as the primary seed for key generation.  

The key file will be created as `$HOME/.credparser/master.seed` the first time a credential string is created by default.  

If the `master.seed` file changes or is moved, any existing credential strings will fail to decode.  The `master.seed` file should be protected as read-only by the user, similar to SSH keys (`chmod 600 master.seed`).  

Credential strings are also signed by the OS-level username.  The `master.seed` file can be moved to other systems, but the OS-level username must remain the same for decoding to succeed.


## Usage Examples

### Interactive CLI - Create Credential String

For manual credential generation, use the interactive CLI tool:

```bash
credparser-make
# Prompts for username/label and password
# Outputs encoded credential string
```

### Programmatic - Create Credentials in Code

```python
from credparser import CredParser

# Create credentials from username and password
creds = CredParser(username="username", password="password")
print(creds.credentials)  # Encoded credential string
```

### Programmatic - Decode Credentials from String

```python
from credparser import CredParser

credential_string = 'abcdefgHIJkILMNO01234596pa=='
creds = CredParser(credentials=credential_string)
print(f'username={creds.username}, password={creds.password}')
```

## Advanced Features

### Alternative Master Seed

An alternative `master.seed` file/location can be specified during CredParser() initialization by supplying an argument for `seed_path`:

```python
# Custom seed file at /opt/secrets/username/master.seed
custom_creds = CredParser(
    username = "admin",
    password = "secret123",
    seed_path=f'/opt/secrets/{getpass.getuser()}/master.seed'
)
secret = custom_creds.credentials

# Trying to load with default master.seed path will raise DecodeFailure
creds = CredParser(credentials=secret)
```

Raises Exception:
```
credparser.errors.DecodeFailure: Invalid credential string, unable to decode
```

### Encoding Customization/Configuration

The internal encoding algorithm can be tuned via the `credparser-config` command or programmatically. Configuration controls salt length and hash round settings used for key derivation.

**Interactive Configuration (manual setup):**

```bash
credparser-config
# Prompts for salt length and min/max hash rounds
```

**Non-interactive Configuration (deployment automation):**

```bash
credparser-config --salt-len 16 --min-hash 10 --max-hash 50
```

**View Current Configuration:**

```bash
credparser-config --test
credparser-config --help
```

**Programmatic Configuration:**

```python
from credparser.guide import configure_credparser

# Interactive mode (prompts user for values)
configure_credparser()

# Non-interactive mode (for deployment scripts and CI/CD)
configure_credparser(salt_len=16, min_hash_rounds=10, max_hash_rounds=50)
```

**Configurable Values:**
```
SALT_LEN              Length of salt values (Default: 12, Minimum: 8)
MIN_HASH_ROUNDS       Min key generation iterations (Default: 3, Minimum: 1)
MAX_HASH_ROUNDS       Max key generation iterations (Default: 24)
```

**Important:** Changes to configuration values will invalidate all previously encoded credentials. Only modify settings during initial deployment or when regenerating all credential strings.


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
import os
import requests
from dotenv import load_dotenv
from credparser import CredParser

# Load environment configuration
load_dotenv()
stored_cred_string = os.getenv('EXAMPLE_CREDENTIALS')

# Decode credentials
creds = CredParser(credentials=stored_cred_string)

# Use with REST API
response = requests.get(
    'https://api.example.com/data',
    auth=(creds.username, creds.password)
)
```