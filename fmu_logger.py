
import os
import sys
from contextlib import contextmanager

def setup_logging(log_file="fmu_output.log"):
    """
    Set up logging to both console and file.
    
    Parameters:
        log_file (str): Path to the log file. Default is 'fmu_output.log'.
        
    Returns:
        file: The opened log file object (needs to be closed later)
    """
    class Logger(object):
        def __init__(self, filename):
            self.terminal = sys.stdout
            self.log = open(filename, "a")

        def write(self, message):
            self.terminal.write(message)
            self.log.write(message)

        def flush(self):
            self.terminal.flush()
            self.log.flush()

    log_file = os.path.abspath(log_file)
    logger = Logger(log_file)
    sys.stdout = logger
    sys.stderr = logger
    
    print(f"\n\n{'='*50}")
    print(f"New session started. Logging to: {log_file}")
    print(f"{'='*50}\n")
    
    return logger.log


@contextmanager
def capture_c_stdout(log_file="fmu_output.log"):
    """Context manager to capture both Python and C-level stdout"""
    # Save original file descriptors
    original_stdout_fd = sys.stdout.fileno()
    original_stderr_fd = sys.stderr.fileno()
    
    # Save original Python stdout/stderr
    original_stdout = sys.stdout
    original_stderr = sys.stderr
    
    # Create a temporary file descriptor
    log_fd = os.open(log_file, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o644)
    
    # Duplicate the original stdout fd
    saved_stdout_fd = os.dup(original_stdout_fd)
    
    try:
        # Redirect stdout and stderr to our log file
        os.dup2(log_fd, original_stdout_fd)
        os.dup2(log_fd, original_stderr_fd)
        
        # Also redirect Python's sys.stdout and sys.stderr
        sys.stdout = open(log_file, 'a')
        sys.stderr = sys.stdout
        
        yield  # This is where your code runs
        
    finally:
        # Restore original file descriptors
        os.dup2(saved_stdout_fd, original_stdout_fd)
        
        # Close duplicated descriptors
        os.close(saved_stdout_fd)
        os.close(log_fd)
        
        # Restore Python's stdout/stderr
        sys.stdout = original_stdout
        sys.stderr = original_stderr