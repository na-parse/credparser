'''
credparser / seed.py

Provider for the master key seed
'''
import os
import secrets
import stat
from pathlib import Path
from .errors import InitFailure

CREDPARSER_SEED_FILE = (
    Path().home() / '.credparser/master.seed'
)

class MasterSeed():
    def __init__(self, allow_init: bool = False, seed_path: Path = None):
        ''' 
        Verify seed exists and can be read, otherwise initialize a new value.

        Note that decode operations are dependent on a master seed pre-existing
          so attempts to decode will block init.
        '''
        try:
            self._allow_init = bool(allow_init)

            # Check for manual seed_path override
            if seed_path is not None: self.seed_path = Path(seed_path)
            else: self.seed_path = CREDPARSER_SEED_FILE
            
            if self.seed_path.exists():
                # Verify that the seed data can be read
                _ = self.seed
                return
            
            # Seed is not available
            if not allow_init:
                errmsg = (
                    f'Unable to initialize, master seed file not found: {str(self.seed_path)}'
                )
                raise InitFailure(errmsg)
            
            # Create a new seed
            self._create_credparser_dir()
            self._create_seed_file()
                
        except InitFailure:
                raise
        except Exception as e:
                raise InitFailure(f"Unexpected error during seed initialization: {e}")
    
    def __str__(self):
        return f'MasterSeed(seed_path={str(self.seed_path)})'
    
    def __repr__(self):
        return (
            f'MasterSeed(allow_init={self._allow_init}, '
            f'seed_path={str(self.seed_path)})'
        )
    

    @property
    def seed(self) -> bytes:
        ''' Read and return the master_seed value as bytes '''
        try:
            with open(self.seed_path, 'rb') as f:
                seed_data = f.read()
            return bytes(seed_data)
         
        except (OSError, PermissionError) as e:
            raise InitFailure(f"Failed to read seed file {seed_path}: {e}")


    def _create_credparser_dir(self,) -> None:
        ''' Create the credparse seed storage directory '''
        # Get the parent (dir) for the master_seed file as a Path()
        seed_dir = Path(self.seed_path).parent
        try:
            os.makedirs(seed_dir, mode=0o700, exist_ok=True)
            # Verify permissions in case directory already existed
            current_mode = stat.S_IMODE(os.stat(seed_dir).st_mode)
            if current_mode != 0o700:  os.chmod(seed_dir, 0o700)
        except (OSError, PermissionError) as e:
            errmsg = f"Failed to create/secure directory {str(seed_dir)}: {e}"
            raise InitFailure(errmsg)

    def _create_seed_file(self) -> None:
        ''' Create the credparse master seed file '''
        # Ensure pathlib.Path class format for seed_path
        seed_path = Path(self.seed_path)
        print(f'credpraser: Initializing new master seed value: {str(seed_path)}')
        try:
            if os.path.exists(seed_path):
                errmsg = f'Attempting to reinitialize existing seed: {str(seed_path)}'
                raise InitFailure(errmsg)
            
            # Create new seed file
            seed_data = secrets.token_bytes(1024)
            
            # Set umask temporarily to ensure secure creation
            old_umask = os.umask(0o077)
            try:
                with open(seed_path, 'wb') as f:
                    f.write(seed_data)
            finally:
                os.umask(old_umask)

            # Verify/set file permissions
            current_mode = stat.S_IMODE(os.stat(seed_path).st_mode)
            if current_mode != 0o600:
                os.chmod(seed_path, 0o600)
                    
        except (OSError, PermissionError) as e:
            raise InitFailure(f"Failed to create/secure seed file {seed_path}: {e}")

