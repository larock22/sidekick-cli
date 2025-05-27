"""Key binding handlers for Sidekick UI."""

from prompt_toolkit.key_binding import KeyBindings
from tunacode.utils.process import cancel_current_process


def create_key_bindings() -> KeyBindings:
    """Create and configure key bindings for the UI."""
    kb = KeyBindings()

    # Add escape escape as a specific sequence
    @kb.add("escape", "escape", eager=True)
    def _double_escape(event):
        """Handle double escape to cancel running commands."""
        # Cancel any running process
        cancel_current_process()
        
        # Cancel any running agent task
        if (
            hasattr(event.app, "current_task")
            and event.app.current_task
            and not event.app.current_task.done()
        ):
            event.app.current_task.cancel()
            event.app.invalidate()
        
        # Try to find state_manager through the app
        if hasattr(event.app, "state_manager") and event.app.state_manager:
            if (
                event.app.state_manager.session.current_task 
                and not event.app.state_manager.session.current_task.done()
            ):
                event.app.state_manager.session.current_task.cancel()
    

    @kb.add("enter")
    def _submit(event):
        """Submit the current buffer."""
        event.current_buffer.validate_and_handle()

    @kb.add("c-o")  # ctrl+o
    def _newline(event):
        """Insert a newline character."""
        event.current_buffer.insert_text("\n")
    
    # Add escape followed by enter for newline (as mentioned in placeholder)
    @kb.add("escape", "enter")
    def _escape_enter(event):
        """Insert a newline when escape then enter is pressed."""
        event.current_buffer.insert_text("\n")

    return kb
