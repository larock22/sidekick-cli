"""File reference completer for @file syntax."""

import os
from typing import Iterable

from prompt_toolkit.completion import CompleteEvent, Completer, Completion
from prompt_toolkit.document import Document


class FileReferenceCompleter(Completer):
    """Completer for @file references that provides file path suggestions."""

    def get_completions(
        self, document: Document, complete_event: CompleteEvent
    ) -> Iterable[Completion]:
        """Get completions for @file references."""
        # Get the word before cursor
        word_before_cursor = document.get_word_before_cursor(WORD=True)
        
        # Check if we're in an @file reference
        if not word_before_cursor.startswith("@"):
            return
            
        # Get the path part after @
        path_part = word_before_cursor[1:]  # Remove @
        
        # Determine directory and prefix
        if "/" in path_part:
            # Path includes directory
            dir_path = os.path.dirname(path_part)
            prefix = os.path.basename(path_part)
        else:
            # Just filename, search in current directory
            dir_path = "."
            prefix = path_part
            
        # Get matching files
        try:
            if os.path.exists(dir_path) and os.path.isdir(dir_path):
                for item in sorted(os.listdir(dir_path)):
                    if item.startswith(prefix):
                        full_path = os.path.join(dir_path, item) if dir_path != "." else item
                        
                        # Skip hidden files unless explicitly requested
                        if item.startswith(".") and not prefix.startswith("."):
                            continue
                            
                        # Add / for directories
                        if os.path.isdir(full_path):
                            display = item + "/"
                            completion = full_path + "/"
                        else:
                            display = item
                            completion = full_path
                            
                        # Calculate how much to replace
                        start_position = -len(path_part)
                        
                        yield Completion(
                            text=completion,
                            start_position=start_position,
                            display=display,
                            display_meta="dir" if os.path.isdir(full_path) else "file"
                        )
        except (OSError, PermissionError):
            # Silently ignore inaccessible directories
            pass