import functools
import logging
from typing import Callable
from queue import Queue
import threading

import adsk.core, adsk.fusion  # pylint:disable=import-error

from ...libs.fusion_addin_framework import fusion_addin_framework as faf
from ... import config
from .ui import InputsWindow, InputIds, FusionDisplay
from .logic_model import {{cookiecutter.command_name}}Model


class {{cookiecutter.command_name}}Command(faf.AddinCommandBase):
    def __init__(self, addin: faf.FusionAddin):

        workspace = faf.Workspace(addin, id=config.{{cookiecutter.command_name.upper()}}_WORKSPACE_ID)
        tab = faf.Tab(workspace, id=config.{{cookiecutter.command_name.upper()}}_TAB_ID)
        panel = faf.Panel(tab, id=config.{{cookiecutter.command_name.upper()}}_PANEL_ID)
        control = faf.Control(panel)

        super().__init__(
            control,
            name=config.{{cookiecutter.command_name.upper()}}_COMMAND_NAME,
            tooltip=config.{{cookiecutter.command_name.upper()}}_TOOLTIP,
        )

        self.model = None

        self.command_window = None
        self.display = None

        self.execution_queue = Queue()
        self._fusion_command: adsk.core.Command = None
        self.last_handler = None
    
    def _executer(self, to_execute: Callable):
        """Utility function which can be used to execute arbitrary FusionAPI calls by automatically
        determining the correct way of executing them. Either via the CustomCommand-doExecute mechanism
        or directly depending on the thread and on the currently active hanler.

        Args:
            to_execute (Callable): The function to execute. Must not accept any arguments.
        """
        # actions from the event must be executed via customEvent(doExecute) (as described in docs)
        # actions from inputChanged handler must be executed via customEvent (otherwise bodies wont get created)
        # actions from commandCreated handler should be executed directly (they might work also with customEvent but not reliable)
        # actions from destroy handler must be executed directly since the command gets already destroyed
        if (
            threading.current_thread() == threading.main_thread()
            and self.last_handler in ("commandCreated", "destroy",)
        ):
            to_execute()
        else:
            self.execution_queue.put(to_execute)
            # FireCustomEvent returns immediately and therefore the lock for actions is removed.
            # The customevent (and the contained doExecute call) is scheduled and might not get immideately executed.
            # Therefore this function might get called (from the periodic thread) again when the execute
            # event is still executed.
            # However, this is not a problem since we can simply put the next ipdate action in the queue.
            adsk.core.Application.get().fireCustomEvent(config.CADTRIS_CUSTOM_EVENT_ID)

    def _track_last_handler(meth: Callable):  # pylint:disable=no-self-argument
        """Method decorator which sets the self.last_handler property to the name of the decorated method.
        """
        @functools.wraps(meth)
        def wrapper(self: "{{cookiecutter.command_name}}Command", *args, **kwargs):
            self.last_handler = meth.__name__
            return meth(self, *args, **kwargs)

        return wrapper

    @_track_last_handler
    def commandCreated(self, eventArgs: adsk.core.CommandCreatedEventArgs):
        self._fusion_command = eventArgs.command

        # change design type to direct design type
        design = adsk.core.Application.get().activeDocument.design
        if design.designType == adsk.fusion.DesignTypes.ParametricDesignType:
            dialog_result = adsk.core.Application.get().userInterface.messageBox(
                config.CADTRIS_DIRECT_DESIGN_QUESTION,
                config.CADTRIS_DIRECT_DESIGN_TITLE,
                adsk.core.MessageBoxButtonTypes.YesNoButtonType,
            )
            if dialog_result == adsk.core.DialogResults.DialogYes:
                design.designType = adsk.fusion.DesignTypes.DirectDesignType
            else:
                return

        # hide ok button
        eventArgs.command.isOKButtonVisible = False

        # fusion_command must be saved as attribute otherwise it will get evaluated at call time 
        # when the eventArgs.command value might have changed or become invalid. 
        faf.utils.create_custom_event(
            config.CADTRIS_CUSTOM_EVENT_ID,
            lambda _: self._fusion_command.doExecute(False),
        )

        comp = faf.utils.new_component(config.CADTRIS_COMPONENT_NAME)
        design.rootComponent.allOccurrencesByComponent(comp).item(0).activate()
        command_window = InputsWindow(eventArgs.command)
        self.display = FusionDisplay(command_window, comp, self._executer)

        self.game = {{cookiecutter.command_name}}Model(self.display)

    @_track_last_handler
    def inputChanged(self, eventArgs: adsk.core.InputChangedEventArgs):
        # do NOT use: inputs = event_args.inputs (will only contain inputs of the same input group as the changed input)
        # use instead: inputs = event_args.firingEvent.sender.commandInputs
        logging.getLogger(__name__).info(f"Changed input: {eventArgs.input}")
        # if eventArgs.input.id == InputIds.<input_name>.value:
        #     pass

    def execute(
        self, eventArgs: adsk.core.CommandEventArgs  # pylint:disable=unused-argument
    ):
        c = 0
        while not self.execution_queue.empty():
            self.execution_queue.get()()
            c+=1
        logging.getLogger(__name__).debug(f"Executed {c} actions.")

    @_track_last_handler
    def destroy(
        self, eventArgs: adsk.core.CommandEventArgs  # pylint:disable=unused-argument
    ):
        # at first game must be terminated to avoid further thread calls while display is cleared
        self.game.terminate()

        if not eventArgs.command.commandInputs.itemById(
            InputIds.KeepBodies.value
        ).value:
            self.display.clear_world()

        self.execution_queue = Queue()

    @_track_last_handler
    def keyDown(self, eventArgs: adsk.core.KeyboardEventArgs):
        logging.getLogger(__name__).info(f"Pressed key {eventArgs.keyCode}.")
        {
            # TODO key-action-mapping
        }.get(eventArgs.keyCode, lambda: None)()

