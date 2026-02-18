from typing import Any

from mods_base import build_mod, hook
from unrealsdk.unreal import UObject

STARTUP_NotStarted = 0


@hook("WillowGame.WillowGFxMoviePressStart:extBeginWait")
def begin_wait(obj: UObject, *_: Any) -> bool:
    if obj.CurrentStartupStep == STARTUP_NotStarted:
        obj.CustomPlay("out")


build_mod()
