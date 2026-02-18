from typing import Any

import unrealsdk
from mods_base import hook, register_mod

STARTUP_NotStarted = 0


@hook("WillowGame.WillowGFxMoviePressStart:extBeginWait")
def begin_wait(obj: unrealsdk.UObject, *_: Any) -> bool:
    if obj.CurrentStartupStep == STARTUP_NotStarted:
        obj.CustomPlay("out")


register_mod()
