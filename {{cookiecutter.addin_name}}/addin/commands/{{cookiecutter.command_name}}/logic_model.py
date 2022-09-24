import threading
from typing import Dict


class {{cookiecutter.command_name}}Model:
    def __init__(self, display: {{cookiecutter.command_name}}Display) -> None:
        """Creates a game according to the settings. Calls the displays upate function once.

        Args:
            display ({{cookiecutter.command_name}}Display): The display which controls how the game is visualized.
        """
        self._display = display

        self._action_lock = threading.Lock()

        self._update_display()

    def _serialize(self) -> Dict:
        """Creates a serialized version of the current game state. This serialization contains
        only primitive datatype but contains all information to visualize the game or rebuild it.
        All containers are deepcopied to avoid a manipulation of the game state from "outside".

        Returns:
            Dict: The serialized game.
        """
        return {
            # TODO serialize self
        }

    def _update_display(self):
        """Calls the update function of the display with the serialized game."""
        self._display.update(self._serialize())
