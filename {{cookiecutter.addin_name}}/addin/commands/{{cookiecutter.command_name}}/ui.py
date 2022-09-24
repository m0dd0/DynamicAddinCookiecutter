from enum import auto
from typing import Dict, Callable
from abc import ABC, abstractmethod
import functools

import adsk.core, adsk.fusion

from ...libs.fusion_addin_framework import fusion_addin_framework as faf
from ...libs.voxler import voxler as vox

from ... import config


class InputIds(faf.utils.InputIdsBase):
    Group1 = auto()
    Button1 = auto()


class InputsWindow:
    def __init__(self, command):
        self._command = command

        self._create_group_1()

    def _create_group_1(self):
        self.controls_group = self._command.commandInputs.addGroupCommandInput(
            InputIds.Group1.value, "Group1"
        )

        self.button_1 = self.controls_group.children.addBoolValueInput(
            InputIds.Button1.value, "Button 1", True
        )

class {{cookiecutter.command_name}}Display(ABC):
    def __init__(self) -> None:
        pass

    @abstractmethod
    def update(self, serialized_model: Dict):
        raise NotImplementedError()

class AsciiDisplay({{cookiecutter.command_name}}Display):
    def __init__(self) -> None:
        super().__init__()

class FusionDisplay({{cookiecutter.command_name}}Display):
    def __init__(
        self,
        command_window: InputsWindow,
        component: adsk.fusion.Component,
        executer: Callable,
    ) -> None:
        """Display abstraction to visualite the game within Fusion360. This takes care of biulding
        the BREPBodies, executing the command for building etc.

        Args:
            command_window (InputsWindow): The command input window which get updated by the display due to
                changes in game state etc.
            component (adsk.fusion.Component): The Fusion360 component into which the blocks are build.
            executer (Callable): A function which takes a single Callable as inputs and executes it
                in a appropriate way.
        """
        self._command_window = command_window

        self._voxel_world = vox.VoxelWorld(config.CADTRIS_INITIAL_VOXEL_SIZE, component)

        self._last_game = None
        self._last_voxels = set()

        self.executer = executer

        super().__init__()

    def _with_executer(meth: Callable):  # pylint:disable:=no-self-argument
        """Decorator for methods which executes the decorated method via the self.executer object."""

        @functools.wraps(meth)
        def wrapper(self: "FusionDisplay", *args, **kwargs):
            self.executer(
                lambda: meth(self, *args, **kwargs)  # pylint:disable=not-callable
            )

        return wrapper

    def _get_voxel_dict(self, serialized_game: Dict) -> Dict:
        """Takes the needed information from the serialized game and transforms them into dictionary
        qith all voxel description which can get passed directly to the voxler-world instance.

        Args:
            serialized_game (Dict): The serialized game.

        Returns:
            Dict: The voxel description for the voxler. {(x_game,y_game):(r,b,g,o)}
        """
        # TODO create xoel dict compatible with voxler

    def _update_voxels(self, serialized_game: Dict):
        """Calls the voxel_world update mechanism and determines whether to use a progressbar or not.

        Args:
            serialized_game (Dict): The serialized game.
        """
        voxels = self._get_voxel_dict(serialized_game)
        n_voxel_diff = len(set(self._last_voxels).symmetric_difference(set(voxels)))
        self._last_voxels = voxels
        progressbar = None
        if n_voxel_diff >= config.{{cookiecutter.command_name.upper()}}_MIN_VOXELS_FOR_PROGRESSBAR:
            progressbar = faf.utils.create_progress_dialog(
                title=config.{{cookiecutter.command_name.upper()}}_PROGRESSBAR_TITLE,
                message=config.{{cookiecutter.command_name.upper()}}_PROGRESSBAR_MESSAGE,
            )
        self._voxel_world.update(
            voxels, progressbar, config.CADTRIS_VOXEL_CHANGES_FOR_DIALOG
        )

    @_with_executer
    def update(self, serialized_game: Dict) -> None:
        """Steps to execute in order to update the screen accordingly. This includes updating the inputs and
        updating the voxel world.
        Depending on the context this function must be executed from the execute event handler or
        directly which is decided in the update-method.

        Args:
            serialized_game (Dict): The serialized game.
        """

        if not self._last_game:
            changes = {k: True for k in serialized_game}
        else:
            changes = {k: v != self._last_game[k] for k, v in serialized_game.items()}

        # TODO implement update mechanism

        self._last_game = serialized_game

    @_with_executer
    def set_grid_size(self, new_grid_size: int):
        """Updates the grid size of the voxel world and updates the camera accordingly in case the current
        game state allows for this action.

        Args:
            new_grid_size (int): _description_
        """
        # if "change" in self._last_game["allowed_actions"]:
        self._voxel_world.set_grid_size(
            new_grid_size,
            faf.utils.create_progress_dialog(
                title=config.{{cookiecutter.command_name.upper()}}_PROGRESSBAR_TITLE,
                message=config.{{cookiecutter.command_name.upper()}}_PROGRESSBAR_MESSAGE,
            ),
        )
            # self._set_camera(self._last_game["height"], self._last_game["width"])

    @_with_executer
    def clear_world(self):
        """Clears all voxels in the used voxel world and also removes the component of the voxel world."""
        self._voxel_world.clear()
        faf.utils.delete_component(self._voxel_world.component)

