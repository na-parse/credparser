# credparser Design notes

## Objective

Obfuscation.

### The Problem

As you start writing scripts to interact with end-points, you will inevitably be faced with the following conundrum:

```
My scripts need to contain end-point credentials, but storing them in the script/in plain text is bad!
```

### General Guidance

Online guidance will suggest using `keyring` - And you should!  However `keyring` only really works for users.  You're trying to get your scripts setup to run unattended for some quick reporting and monitoring.  Making `keyring` work for unattended scheduled scripts is possible, but more complex.

The next suggestion is to use a secrets management system.  While a good idea, at the end of the day, you're still going to be doing something like placing an API key in plaintext in your profile, environment, or some other configuration location.  And that key accesses _the vault_!

### Excessive Complexity Leads to Disaster

You're just trying to write some scripts to use these handy REST end points to automate some of the stuff you're doing manually, you're not in a position to engineer a full organization wide secrets management system.

No, you've got work to do, so you just embed the username and password in a config file, load them into environment variables in your .profile.

This is _the problem_.

## CredParser Solution

You need the credentials available to load, but you don't want to save them in plain text.

The `credparser` package provides a quick solution to apply basic symmetric encryption using heuristically derived keys based around a master seed file that can be secured by the user.

The `CredParser` class will convert a username/password pair into an encrypted bytes package, presented in base64 for text compatibility.  Loading that credential string back into a `CredParser` object will allow it to return the username and password.

The username and password values are derived dynamically via class properties to avoid in-memory storage.  Only the encrypted credential string is stored.

### CredParser Weakness

Similar to every other basic roll-your-own schema, credparser is based around a predictable key generation process, using the key to XOR the message, without any robust padding, mixing, or other standard elements of a solid encryption program.

The CredParser algorithm uses a public/private approach to encryption, using the master.seed as the 'private' part of the key-gen process, while the 'salt' is actually exposed as a header in the credential string as the 'public' part of the key-gen.

In short, retrieval of a user's master.seed file would allow the decryption of any credential string it was used to generate.

### Obfuscation, not Security

As a result, the use of `credparser` is intended to provide an additional mask to your existing security suite, but is not intended to provide a secure enclave for credentials.  

Use of `credparser` should adhere to the following guidelines

- Only deploy on secured systems with limited access

Systems with encoded credentials should already have other security precautions in place to ensure minimum access necessary standards.  Do not use on systems with exposed services or shared infrastructure.

- Only encode restricted service account credentials

Best practice is to create service accounts for the targeted services with the least access necessary.  As an example, if your scripts will only be generating reporting for a network service, the account used to access that service should only have read-only access to that network service, and no other rights to anything else in your environment.

This limits attack surface if the encoded credentials are exposed.

## Encryption Details

More to come, my dog is whining.