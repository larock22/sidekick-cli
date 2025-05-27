"""Key binding handlers for Sidekick UI."""

import time
from prompt_toolkit.key_binding import KeyBindings
from tunacode.utils.process import cancel_current_process


# Track escape key presses for double-tap detection
_last_escape_time = 0
_escape_timeout = 0.5  # 500ms timeout for double-tap


def create_key_bindings() -> KeyBindings:
    """Create and configure key bindings for the UI."""
    kb = KeyBindings()

    @kb.add("escape", eager=True)
    def _cancel(event):
        """Handle escape key - double tap to cancel running commands."""
        global _last_escape_time
        
        current_time = time.time()
        time_since_last = current_time - _last_escape_time
        
        if time_since_last < _escape_timeout:
            # Double escape detected - cancel any running process
            cancel_current_process()
            
            # Also cancel any running agent task
            if (
                hasattr(event.app, "current_task")
                and event.app.current_task
                and not event.app.current_task.done()
            ):
                event.app.current_task.cancel()
                event.app.invalidate()
            
            # Reset the timer
            _last_escape_time = 0
            
            # Visual feedback will be shown by the cancelled command itself
        else:
            # First escape - record the time
            _last_escape_time = current_time
            
            # For now, no visual feedback on first escape to avoid clutter

    @kb.add("enter")
    def _submit(event):
        """Submit the current buffer."""
        event.current_buffer.validate_and_handle()

    @kb.add("c-o")  # ctrl+o
    def _newline(event):
        """Insert a newline character."""
        event.current_buffer.insert_text("\n")

    return kb
