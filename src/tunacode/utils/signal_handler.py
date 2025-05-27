"""Global signal handling for command cancellation."""

import signal
import sys
import time
from typing import Optional

from .process import cancel_current_process


class DoubleInterruptHandler:
    """Handle double Ctrl+C or signal interrupts to cancel running commands."""
    
    def __init__(self, timeout: float = 0.5):
        self.timeout = timeout
        self.last_interrupt_time = 0
        self.original_handler = None
        self.state_manager = None
        
    def set_state_manager(self, state_manager):
        """Set the state manager for task cancellation."""
        self.state_manager = state_manager
        
    def handle_interrupt(self, signum, frame):
        """Handle interrupt signal."""
        current_time = time.time()
        time_since_last = current_time - self.last_interrupt_time
        
        if time_since_last < self.timeout:
            # Double interrupt detected
            print("\n⚠️  Cancelling command...")
            
            # Cancel any running subprocess
            cancel_current_process()
            
            # Cancel agent task if available
            if self.state_manager and hasattr(self.state_manager.session, 'current_task'):
                task = self.state_manager.session.current_task
                if task and not task.done():
                    task.cancel()
            
            # Reset timer
            self.last_interrupt_time = 0
            
            # Don't propagate the signal further
            return
        else:
            # First interrupt
            self.last_interrupt_time = current_time
            print("\n(Press Ctrl+C again to cancel command)")
            
            # Don't exit on first Ctrl+C
            return
    
    def install(self):
        """Install the signal handler."""
        if sys.platform != "win32":
            # Unix-like systems
            self.original_handler = signal.signal(signal.SIGINT, self.handle_interrupt)
        else:
            # Windows - Ctrl+C is handled differently
            signal.signal(signal.SIGINT, self.handle_interrupt)
    
    def uninstall(self):
        """Restore original signal handler."""
        if self.original_handler is not None:
            signal.signal(signal.SIGINT, self.original_handler)


# Global instance
double_interrupt_handler = DoubleInterruptHandler()