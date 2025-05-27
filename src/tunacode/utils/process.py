"""Utilities for process management with cancellation support."""

import asyncio
import os
import signal
import subprocess
import sys
from typing import Optional, Tuple


class CancellableProcess:
    """Wrapper for subprocess that supports cancellation."""
    
    def __init__(self):
        self.process: Optional[subprocess.Popen] = None
        self._cancelled = False
    
    async def run(self, command: str, shell: bool = True) -> Tuple[str, str, int]:
        """
        Run a command with cancellation support.
        
        Args:
            command: Command to run
            shell: Whether to use shell
            
        Returns:
            Tuple of (stdout, stderr, returncode)
        """
        self._cancelled = False
        
        # Start the process
        self.process = subprocess.Popen(
            command,
            shell=shell,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            # Create new process group for proper signal handling
            preexec_fn=os.setsid if sys.platform != "win32" else None,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0
        )
        
        try:
            # Run the process in an executor to make it async
            loop = asyncio.get_event_loop()
            stdout, stderr = await loop.run_in_executor(
                None, self.process.communicate
            )
            
            if self._cancelled:
                return "", "Process cancelled by user", -1
                
            return stdout or "", stderr or "", self.process.returncode
            
        except asyncio.CancelledError:
            # Handle cancellation
            self.cancel()
            raise
    
    def cancel(self):
        """Cancel the running process."""
        self._cancelled = True
        if self.process and self.process.poll() is None:
            try:
                if sys.platform == "win32":
                    # On Windows, use terminate
                    self.process.terminate()
                else:
                    # On Unix, kill the process group
                    os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
                
                # Give it a moment to terminate gracefully
                try:
                    self.process.wait(timeout=0.5)
                except subprocess.TimeoutExpired:
                    # Force kill if it doesn't terminate
                    if sys.platform == "win32":
                        self.process.kill()
                    else:
                        os.killpg(os.getpgid(self.process.pid), signal.SIGKILL)
            except (ProcessLookupError, PermissionError):
                # Process already terminated
                pass


# Global process manager for the current command
_current_process: Optional[CancellableProcess] = None


def get_current_process() -> Optional[CancellableProcess]:
    """Get the current running process."""
    return _current_process


def set_current_process(process: Optional[CancellableProcess]):
    """Set the current running process."""
    global _current_process
    _current_process = process


def cancel_current_process():
    """Cancel the current running process if any."""
    if _current_process:
        _current_process.cancel()