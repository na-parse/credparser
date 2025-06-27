import pytest

from credparser import CredParser
from credparser import mutators
from credparser.errors import *


def test_credparser_init_username_password():
    parser = CredParser(username="user", password="password")
    assert parser.username == "user"
    assert parser.password == "password"
    assert parser.credentials is not None

def test_credparser_init_empty_username():
    parser = CredParser(username="", password="password")
    assert parser.username == ""
    assert parser.password == "password"
    assert parser.credentials is not None

def test_credparser_init_empty_password():
    parser = CredParser(username="user", password="")
    assert parser.username == "user"
    assert parser.password == ""
    assert parser.credentials is not None

def test_credparser_init_empty_username_and_password():
    parser = CredParser(username="", password="")
    assert parser.username == ""
    assert parser.password == ""
    assert parser.credentials is not None


def test_credparser_load_credentials():
    parser1 = CredParser(username="user", password="password")
    encoded_creds = parser1.credentials
    parser2 = CredParser()
    parser2.load(encoded_creds)
    assert parser2.username == "user"
    assert parser2.password == "password"

def test_credparser_reset_credentials():
    parser = CredParser(username="user", password="password")
    original_credentials = parser.credentials
    parser.reset(username="newuser", password="newpassword")
    assert parser.username == "newuser"
    assert parser.password == "newpassword"
    assert parser.credentials != original_credentials

    

def test_credparser_init_credentials():
    # Testing known encoded value decode
    # - This expects a SALT_LEN of 12, master of TESTING
    orig_SALT_LEN = mutators.SALT_LEN
    mutators.SALT_LEN = 12
    encoded_creds = 'YFej9Q00Dcob3QsCh/Nt+dotgYeiOy1wtgsnZwH3qtTqvQ=='
    master = 'TESTING'
    username, password = mutators._decode(encoded_creds,master)
    mutators.SALT_LEN = orig_SALT_LEN
    assert username == "user"
    assert password == "password"


def test_credparser_init_no_args():
    parser = CredParser()
    assert parser.username is None
    assert parser.password is None


def test_credparser_init_invalid_credentials():
    with pytest.raises(InvalidCredentialString):
        CredParser(credentials="invalid-base64-string")


def test_credparser_init_username_only_fails():
    with pytest.raises(UsageError):
        CredParser(username="user")


def test_credparser_init_password_only_fails():
    with pytest.raises(UsageError):
        CredParser(password="password")


def test_credparser_init_both_creds_and_user_pass_fails():
    with pytest.raises(UsageError):
        CredParser(username="user", password="password", credentials="abc")




def test_credparser_load_invalid_credentials():
    parser = CredParser()
    with pytest.raises(InvalidCredentialString):
        parser.load("invalid-string")

def test_credparser_readonly_attributes():
    parser = CredParser()
    with pytest.raises(AttributeError):
        parser.username = "username"
        parser.password = "password"
        parser.credentials = "invalid-string"

