# credparser Embedded Credential Parsing

`credparser` is intended to provide automation systems with end-point credential requirements the ability to embed credential values in a non-plain-text format.

## The Problem

Secret managers are the way to go.  The `keyring` solution exists as well.  But at the end of the day, my observation has been that for small, quick REST access scripts, everyone seems to be loading plain user/password values from text files, environment variables (which are generally populated from plain text files), or some other clunky solution.

Secret managers highly complicate lightweight scripts and establish a significant barrier to entry for initial developments, keyring only really works for interactive users, and if you're loading environment from plain text, your credentials are still out there somewhere in plain text.

## credparser's Approach

You:
- Need to load a config file
- Config file needs to contain credentials
- Agree that credentials should never be stored in plain text

`credparser`:
- Basic hash encryption
- Fingerprint based on system and user information
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

