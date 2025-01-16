from typing import Any

import unrealsdk
from unrealsdk.hooks import Block
from unrealsdk.unreal import BoundFunction, UObject, WrappedStruct

from mods_base import BoolOption, build_mod, get_pc, hook, keybind
from ui_utils import show_hud_message

auto_skip_option = BoolOption("Autoskip Dialog", value=False)


@keybind("Toggle Autoskip")
def toggle_autoskip() -> None:
    auto_skip_option.value = not auto_skip_option.value
    show_hud_message("Autoskip", f"Autoskip is now {'on' if auto_skip_option.value else 'off'}")


@keybind("Skip Dialog")
def skip_dialog() -> None:
    for dialog in unrealsdk.find_all("GearboxDialogComponent"):
        dialog.StopTalking()


def is_obj_allowed_to_talk(obj: UObject) -> bool:
    if obj.Class._inherits(unrealsdk.find_class("WillowPlayerPawn")):
        return True
    if obj.Class._inherits(unrealsdk.find_class("WillowAIPawn")) and get_pc().Pawn.IsEnemy(obj):
        return True
    if obj.Class._inherits(unrealsdk.find_class("WillowVendingMachine")):  # noqa: SIM103
        return True
    return False


@hook("GearboxFramework.Behavior_TriggerDialogEvent:TriggerDialogEvent")
@hook("GearboxFramework.WillowDialogAct_Talk:Activate")
@hook("GearboxFramework.GearboxDialogComponent:TriggerEvent")
def dialog(
    obj: UObject,
    args: WrappedStruct,
    _3: Any,
    _4: BoundFunction,
) -> Block | None:
    if obj.Class._inherits(
        unrealsdk.find_class("Behavior_TriggerDialogEvent"),
    ) and is_obj_allowed_to_talk(
        args.ContextObject,
    ):
        return None
    if obj.Class._inherits(
        unrealsdk.find_class("WillowDialogAct_Talk"),
    ) and is_obj_allowed_to_talk(obj.GetActor()):
        return None
    if obj.Class._inherits(
        unrealsdk.find_class("GearboxDialogComponent"),
    ) and is_obj_allowed_to_talk(obj.Owner):
        return None

    if not auto_skip_option.value:
        return None

    return Block


build_mod()
