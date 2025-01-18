from typing import Any

import unrealsdk
from mods_base import BoolOption, build_mod, get_pc, hook, keybind
from ui_utils import show_hud_message
from unrealsdk.hooks import Block
from unrealsdk.unreal import BoundFunction, UObject, WrappedStruct

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
    if obj.Class._inherits(unrealsdk.find_class("WillowAIPawn")) and not get_pc().Pawn.IsEnemy(obj):
        return False
    if obj.Class._inherits(unrealsdk.find_class("WillowDialogEchoActor")):  # noqa: SIM103
        return False
    return True


def try_skip(obj: UObject) -> Block | None:
    return Block if not is_obj_allowed_to_talk(obj) else None


@hook("GearboxFramework.Behavior_TriggerDialogEvent:TriggerDialogEvent")
def trigger_dialog_event(
    _1: UObject,
    args: WrappedStruct,
    _3: Any,
    _4: BoundFunction,
) -> Block | None:
    return try_skip(args.ContextObject)


@hook("WillowGame.WillowDialogAct_Talk:TalkStarted")
def activate(
    obj: UObject,
    args: WrappedStruct,
    _3: Any,
    _4: BoundFunction,
) -> Block | None:
    actor = args.InTalker
    if not is_obj_allowed_to_talk(actor) and hasattr(actor, "DialogComponent"):
        actor.DialogComponent.StopTalking()


@hook("GearboxFramework.GearboxDialogComponent:TriggerEvent")
def trigger_event(
    obj: UObject,
    _2: WrappedStruct,
    _3: Any,
    _4: BoundFunction,
) -> Block | None:
    return try_skip(obj.Owner)


build_mod()
