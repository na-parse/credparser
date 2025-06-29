import pytest

from credparser import CredParser
from credparser import mutators
from credparser.errors import *
from credparser.config import CredParserConfig, config
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
    config = CredParserConfig(config_file=Path(__file__).parent / 'dot_config_test_good')
    assert config.salt_len == 20
    assert config.max_hash_rounds == 56
    assert config.min_hash_rounds == 12

def test_credparser_config_file_missing():
    config = CredParserConfig(config_file=Path(__file__) / 'bad_file_path')
    assert config.salt_len != None
    assert config.max_hash_rounds != None
    assert config.min_hash_rounds != None


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
        CredParser(username="user", password="password", credentials="abc", seed_path=TEST_SEED_PATH)

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
        config = CredParserConfig(config_file=Path(__file__).parent / 'dot_config_test_salt')

def test_credparser_config_min_hash_rounds_fails():
    with pytest.raises(ConfigError):
        config = CredParserConfig(config_file=Path(__file__).parent / 'dot_config_test_min_hash')

def test_credparser_config_min_higher_than_max_hash_rounds_fails():
    with pytest.raises(ConfigError):
        config = CredParserConfig(config_file=Path(__file__).parent / 'dot_config_test_minmax_hash')


# Cleanup fixture - runs after all tests complete
@pytest.fixture(scope="module", autouse=True)
def cleanup_test_directory():
    '''Cleanup test directory after all tests complete'''
    yield
    test_dir = TEST_SEED_PATH.parent
    if test_dir.exists():
        shutil.rmtree(test_dir)
