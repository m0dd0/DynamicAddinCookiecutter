"""This file contains constants which hold all kinds of settings or user interface stings etc."""

from pathlib import Path

# logging settings
LOGGING_FOLDER = Path(__file__).parent.parent / "logs"
LOGFILE_BASENAME = "{{cookiecutter.command_name}}.log"
LOGGING_ENABLED = True
LOGGING_ROTATE_WHEN = "H"
LOGGING_ROTATE_INTERVAL = 6
LOGGING_ROTATE_COUNT = 20

# command settings
{{cookiecutter.command_name.upper()}}_WORKSPACE_ID = "{{cookiecutter.workspace_id}}"
{{cookiecutter.command_name.upper()}}_TAB_ID = "{{cookiecutter.tab_id}}"
{{cookiecutter.command_name.upper()}}_PANEL_ID = "{{cookiecutter.panel_id}}"
{{cookiecutter.command_name.upper()}}_COMMAND_NAME = "{{cookiecutter.command_name}}"
{{cookiecutter.command_name.upper()}}_TOOLTIP = "{{cookiecutter.tooltip}}"

{{cookiecutter.command_name.upper()}}_DIRECT_DESIGN_QUESTION = (
    "WARNING: {{cookiecutter.command_name}} can only be played in direct design mode.\n"
    + "Do you want to switch to direct design mode by disabling the timeline?\n\n"
    + "The timeline and all design history will be removed, \n"
    + "and further operations will not be captured in the timeline."
)
{{cookiecutter.command_name.upper()}}_PROGRESSBAR_TITLE = "Updating Screen"
{{cookiecutter.command_name.upper()}}_MIN_VOXELS_FOR_PROGRESSBAR = 15
