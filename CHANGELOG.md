# Changelog

## [1.1.0] - 2024-12-16

### Added

- Non-interactive mode for `credparser-config` command supporting `--salt-len`, `--min-hash`, and `--max-hash` parameters for deployment automation
- CLI verification option `credparser-config --test` to display current configuration
- `python -m credparser` menu-driven interface for interactive access to CLI tools
- Programmatic configuration support: `configure_credparser(salt_len=X, min_hash_rounds=Y, max_hash_rounds=Z)`
- Comprehensive logging integration across all modules (DEBUG and WARNING levels)
- Enhanced input validation with ASCII compatibility and length enforcement (0-255 characters)

### Changed

- Configuration refactored from class pattern to frozen dataclass with factory function pattern
- Encode/decode implementation refactored to bytes-only internal operations with ASCII boundary encoding
- Updated README with non-interactive deployment examples and CLI parameter documentation
- Modern Python packaging via PEP 517/518 (pyproject.toml with setuptools backend) enabling `pip install` support

### Fixed

- Critical: Undefined variable `self` in config error message (config.py:134)
- Critical: Undefined variable `seed_path` in seed error message (seed.py:66)
- Critical: Typo `credpraser` → `credparser` in seed debug message (seed.py:86)

### Removed

- Deprecated TODO about planned parameter support (now implemented)

---

## [1.0.0] - 2024-12-15

Initial release of credparser with core credential encoding/decoding, master seed management, configuration support, and CLI tools.
