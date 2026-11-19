from mods_base import get_pc
from ui_utils import OptionBox, OptionBoxButton

from .saves import load_player_save

RETURN_BUTTON = OptionBoxButton("Quit", "Return to the main menu.")
CONTINUE_BUTTON = OptionBoxButton("Continue", "Continue playing.")
CONTINUE_PURGE_BUTTON = OptionBoxButton(
    "Continue and Purge", "Continue playing and purge any broken item backups."
)


def on_select(option: OptionBox, button: OptionBoxButton) -> None:
    option.hide()
    pc = get_pc()
    if button == RETURN_BUTTON:
        pc.ReturnToTitleScreen(False)
        return
    if button == CONTINUE_BUTTON:
        return
    save_id = pc.SaveGameFileId
    save_data = load_player_save(save_id)
    save_data["backup"] = {"weapons": {}, "items": {}, "bank": {}}


LOAD_WARNING_BOX = OptionBox(
    title="Warning",
    message="Some items were unable to load.",
    prevent_cancelling=True,
    buttons=[RETURN_BUTTON, CONTINUE_BUTTON, CONTINUE_PURGE_BUTTON],
    on_select=on_select,
)
