# credparser Design notes

## Objective

Obfuscation.

### The Problem

As you start writing scripts to interact with end-points, you will inevitably
be faced with the following conundrum:

```
My scripts need to contain end-point credentials, but storing them in the
script/in plain text is bad!
```

### General Guidance

Online guidance will suggest using `keyring` - And you should!  However
`keyring` only really works for users.  You're trying to get your scripts
setup to run unattended for some quick reporting and monitoring.  Making
`keyring` work for unattended scheduled scripts is possible, but more complex.

The next suggestion is to use a secrets management system.  While a good idea,
at the end of the day, you're still going to be doing something like placing
an API key in plaintext in your profile, environment, or some other
configuration location.  And that key accesses _the vault_!

### Excessive Complexity Leads to Disaster

You're just trying to write some scripts to use these handy REST end points to
automate some of the stuff you're doing manually, you're not in a position to
engineer a full organization wide secrets management system.

No, you've got work to do, so you just embed the username and password in a
config file, load them into environment variables in your .profile.

This is _the problem_.

## CredParser Solution

You need the credentials available to load, but you don't want to save them in
plain text.

The `credparser` package provides a quick solution to apply basic symmetric
encryption using heuristically derived keys based around a master seed file
that can be secured by the user.

The `CredParser` class will convert a username/password pair into an encrypted
bytes package, presented in base64 for text compatibility.  Loading that
credential string back into a `CredParser` object will allow it to return the
username and password.

The username and password values are derived dynamically via class properties
to avoid in-memory storage.  Only the encrypted credential string is stored.

### CredParser Weakness

Similar to every other basic roll-your-own schema, credparser is based around
a predictable key generation process, using the key to XOR the message,
without any robust padding, mixing, or other standard elements of a solid
encryption program.

The CredParser algorithm uses a public/private approach to encryption, using
the master.seed as the 'private' part of the key-gen process, while the 'salt'
is actually exposed as a header in the credential string as the 'public' part
of the key-gen.

In short, retrieval of a user's master.seed file would allow the decryption of
any credential string it was used to generate.

### Obfuscation, not Security

As a result, the use of `credparser` is intended to provide an additional mask
to your existing security suite, but is not intended to provide a secure
enclave for credentials.

Use of `credparser` should adhere to the following guidelines

- Only deploy on secured systems with limited access

Systems with encoded credentials should already have other security
precautions in place to ensure _least-access-required_ standards.  Do not use
on systems with exposed services or shared infrastructure.

- Only encode restricted service account credentials

Best practice is to create service accounts for the targeted services with the
least access necessary.  As an example, if your scripts will only be
generating reporting for a network service, the account used to access that
service should only have read-only access to that network service, and no
other rights to anything else in your environment.

This limits attack surface if the encoded credentials are exposed.

## Encryption Details

Encryption protocol ingredients:

- `master_seed` Byte value read from a specified source file
- `salt` ASCII character set created randomly for each credential string
- `OS-level username` String output from `getpass.getuser()`

### Encode (Encryption) Process

- Random salt is generated
- Key is derived using master_seed, salt, and getpass.getuser()
- Message is assembled as `salt`+`username_len`+`username`+;`password`
- Each message byte is bit order reversed (0010 1110 -> 0111 0100)
- Message is XORed with key
- Cipher Message is base64 encoded
- Credential string returned is `salt`+`cipher_message`

### Key Derivation

Encryption key is generated using the following:

- Salt + getpass.getuser() is converted to bytes
- Master Seed is XORed with the salt+username mask to generate input bytes
- Hash Rounds
  - Salt is converted to an integer
  - salt_int modulo using max_hash_rounds determines number of hash rounds
  - sha512 digest of input bytes is repeated for each hash round
- Final sha512 digest is returned as the key

### Decode Process

- Salt is extracted from credential string using configured salt_len
  - If salt_len changes, decoding will fail due to incorrect salt values
  - Salt is intentionally chosen to blend into base64 character sets
- cipher_message is extracted from base64 string based on salt_len offset
- Master seed loaded from local filesystem source
- `getpass.getuser()` name retrieved
- If salt, seed, and username are the same, key derivation produces the same key
- cipher_message bytes are decrypted using key
- Each message byte is bit-order flipped (0111 0100 -> 0010 1110)
- Message salt is compared to supplied salt to verify accurate decryption
- Username Length is extracted and used to split username and password values
- username and password are returned as a tuple

Note that CredParser uses class properties to retrieve and return username and
password values without assigning them to any static class variables to limit
memory exposure.

### Weakness

The Salt is exposed as part of the key.  Familiarity with the source of the
credentials generator can quickly result in accurate identification of the 
salt component (identify credparser codebase and locate configured salt_len).

Assuming a credential string is compromised, attacker would have high
likelihood of being able to identify what the expected `getpass.getuser()` output
would be as part of the key generation process.

If files containing the credential string are compromised, it is highly likely
the master.seed is compromised as well.

Cipher message data package is a 1-1 character representation.  Additional
cryptographic methods such as padding are not being deployed because they 
would not increase the cipher strength significantly considering the previously
discussed weaknesses.

### Strengths

Credential keys are sufficiently strong to remain secure in any situation
where the string is exposed without access to the user's master.seed.

Multiple credential string compromise would not affect this due to the highly
randomized nature of the sha512 hash method used to generate keys -- No
credential string will be generated using the same key.  Additionally, 
different salts will result in different hash rounds as well, complicating
brute force decoding.

Most situations where the credential string is exposed would result in
compromise of other systems such as keyring, API keys for secret vault
access, etc.

## Closing Notes

Credential strings are sufficiently secure in situations where the deployed
environment is already significantly secured.

Strings should still be treated the same as plain-text username and password
configurations; secure config files, do not embed in shared files,
particularly in code bases.

However, if strings must be included in shared files, separation/segmentation 
of the master.seed file will still prevent exposure of credentials.
