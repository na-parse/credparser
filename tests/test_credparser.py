'''
Test suite for the credparser module
'''
import pytest

from credparser import CredParser
from credparser import mutators
from credparser.errors import *
from credparser.config import CredParserConfig, load_config, config
from pathlib import Path
import shutil

# Set a test-specific path for the master_seed file
TEST_SEED_PATH = Path(__file__).parent.parent / 'test_.credparser' / 'master.seed'
# Make sure test dir isn't left over from previous runs
if TEST_SEED_PATH.parent.exists():
    shutil.rmtree(TEST_SEED_PATH.parent)


def test_credparser_decode_fail_with_no_master():
    # Make sure a decode with no master.seed file fails
    if TEST_SEED_PATH.parent.exists():
        shutil.rmtree(TEST_SEED_PATH.parent)
    with pytest.raises(InitFailure):
        # Verify that decdode refuses to run if master.seed is missing
        parser = CredParser(credentials="credential-string", seed_path=TEST_SEED_PATH)
        

def test_credparser_init_username_password():
    parser = CredParser(username="user", password="password", seed_path=TEST_SEED_PATH)
    assert parser.username == "user"
    assert parser.password == "password"
    assert parser.credentials is not None

def test_credparser_init_empty_username():
    parser = CredParser(username="", password="password", seed_path=TEST_SEED_PATH)
    assert parser.username == ""
    assert parser.password == "password"
    assert parser.credentials is not None

def test_credparser_init_empty_password():
    parser = CredParser(username="user", password="", seed_path=TEST_SEED_PATH)
    assert parser.username == "user"
    assert parser.password == ""
    assert parser.credentials is not None

def test_credparser_init_empty_username_and_password():
    parser = CredParser(username="", password="", seed_path=TEST_SEED_PATH)
    assert parser.username == ""
    assert parser.password == ""
    assert parser.credentials is not None


def test_credparser_load_credentials():
    parser1 = CredParser(username="user", password="password", seed_path=TEST_SEED_PATH)
    encoded_creds = parser1.credentials
    parser2 = CredParser(seed_path=TEST_SEED_PATH)
    parser2.load(encoded_creds)
    assert parser2.username == "user"
    assert parser2.password == "password"

def test_credparser_reset_credentials():
    parser = CredParser(username="user", password="password", seed_path=TEST_SEED_PATH)
    original_credentials = parser.credentials
    parser.reset(username="newuser", password="newpassword")
    assert parser.username == "newuser"
    assert parser.password == "newpassword"
    assert parser.credentials != original_credentials

def test_credparser_init_no_args():
    parser = CredParser()
    assert parser.username is None
    assert parser.password is None


def test_credparser_custom_config():
    cfg = load_config(config_file=Path(__file__).parent / 'dot_config_test_good')
    assert cfg.salt_len == 20
    assert cfg.max_hash_rounds == 56
    assert cfg.min_hash_rounds == 12

def test_credparser_config_file_missing():
    cfg = load_config(config_file=Path(__file__) / 'bad_file_path')
    assert cfg.salt_len is not None
    assert cfg.max_hash_rounds is not None
    assert cfg.min_hash_rounds is not None


def test_credparser_init_invalid_credentials():
    with pytest.raises(DecodeFailure):
        CredParser(credentials="invalid-base64-string", seed_path=TEST_SEED_PATH)


def test_credparser_init_username_only_fails():
    with pytest.raises(UsageError):
        CredParser(username="user", seed_path=TEST_SEED_PATH)


def test_credparser_init_password_only_fails():
    with pytest.raises(UsageError):
        CredParser(password="password", seed_path=TEST_SEED_PATH)


def test_credparser_init_both_creds_and_user_pass_fails():
    with pytest.raises(UsageError):
        CredParser(
            username="user", 
            password="password", 
            credentials="abc", 
            seed_path=TEST_SEED_PATH
        )

def test_credparser_username_too_long_fails():
    with pytest.raises(UsageError):
        CredParser(
            username="a" * 256, 
            password="password", 
            seed_path=TEST_SEED_PATH
        )

def test_credparser_username_max_length():
    parser = CredParser(username="a" * 255, password="password", seed_path=TEST_SEED_PATH)
    assert len(parser.username) == 255

def test_credparser_username_non_ascii_fails():
    with pytest.raises(UsageError):
        CredParser(username="user\u00e9", password="password", seed_path=TEST_SEED_PATH)

def test_credparser_password_non_ascii_fails():
    with pytest.raises(UsageError):
        CredParser(username="user", password="pass\u00e9", seed_path=TEST_SEED_PATH)

def test_credparser_load_invalid_credentials():
    parser = CredParser(seed_path=TEST_SEED_PATH)
    with pytest.raises(DecodeFailure):
        parser.load("invalid-string")

def test_credparser_readonly_attribute_username():
    parser = CredParser(seed_path=TEST_SEED_PATH)
    with pytest.raises(AttributeError):
        parser.username = "username"

def test_credparser_readonly_attribute_password():
    parser = CredParser(seed_path=TEST_SEED_PATH)
    with pytest.raises(AttributeError):
        parser.password = "password"

def test_credparser_readonly_attribute_credentials():
    parser = CredParser(seed_path=TEST_SEED_PATH)
    with pytest.raises(AttributeError):
        parser.credentials = "invalid-string"

def test_credparser_config_salt_len_fails():
    with pytest.raises(ConfigError):
        load_config(config_file=Path(__file__).parent / 'dot_config_test_salt')

def test_credparser_config_min_hash_rounds_fails():
    with pytest.raises(ConfigError):
        load_config(config_file=Path(__file__).parent / 'dot_config_test_min_hash')

def test_credparser_config_min_higher_than_max_hash_rounds_fails():
    with pytest.raises(ConfigError):
        load_config(config_file=Path(__file__).parent / 'dot_config_test_minmax_hash')


def test_credparser_custom_signer_encode_decode():
    # Credentials encoded with a custom signer should decode correctly
    parser = CredParser(
        username="user", password="password",
        signer="custom_signer",
        seed_path=TEST_SEED_PATH
    )
    assert parser.username == "user"
    assert parser.password == "password"
    assert parser.credentials is not None

def test_credparser_custom_signer_stored():
    # The signer value should be accessible on the instance
    parser = CredParser(
        username="user", password="password",
        signer="custom_signer",
        seed_path=TEST_SEED_PATH
    )
    assert parser.signer == "custom_signer"

def test_credparser_custom_signer_wrong_signer_fails():
    # Credentials encoded with one signer cannot be decoded with a different signer
    parser = CredParser(
        username="user", password="password",
        signer="signer_a",
        seed_path=TEST_SEED_PATH
    )
    encoded = parser.credentials
    with pytest.raises(DecodeFailure):
        CredParser(credentials=encoded, signer="signer_b", seed_path=TEST_SEED_PATH)

def test_credparser_custom_signer_default_signer_fails():
    # Credentials encoded with a custom signer cannot be decoded with the default signer
    parser = CredParser(
        username="user", password="password",
        signer="definitely_not_os_user",
        seed_path=TEST_SEED_PATH
    )
    encoded = parser.credentials
    with pytest.raises(DecodeFailure):
        CredParser(credentials=encoded, seed_path=TEST_SEED_PATH)

def test_credparser_load_with_custom_signer():
    # load() should use the signer set on the instance
    parser_enc = CredParser(
        username="user", password="password",
        signer="custom_signer",
        seed_path=TEST_SEED_PATH
    )
    encoded = parser_enc.credentials

    parser_dec = CredParser(signer="custom_signer", seed_path=TEST_SEED_PATH)
    parser_dec.load(encoded)
    assert parser_dec.username == "user"
    assert parser_dec.password == "password"

def test_credparser_reset_with_custom_signer():
    # reset() with a new signer should re-encode under the new signer
    parser = CredParser(
        username="user", password="password",
        signer="signer_a",
        seed_path=TEST_SEED_PATH
    )
    parser.reset(username="newuser", password="newpassword", signer="signer_b")
    assert parser.username == "newuser"
    assert parser.password == "newpassword"
    assert parser.signer == "signer_b"


# Cleanup fixture - runs after all tests complete
@pytest.fixture(scope="module", autouse=True)
def cleanup_test_directory():
    '''Cleanup test directory after all tests complete'''
    yield
    test_dir = TEST_SEED_PATH.parent
    if test_dir.exists():
        shutil.rmtree(test_dir)
