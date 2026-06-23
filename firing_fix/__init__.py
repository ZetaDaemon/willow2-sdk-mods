from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING, Any

from mods_base import BoolOption, build_mod, hook
from unrealsdk import find_class, find_object
from unrealsdk.hooks import Block
from unrealsdk.unreal import BoundFunction, UObject, WrappedStruct

BUTTON_STATE_Pressed = 0
BUTTON_STATE_Held = 1


if TYPE_CHECKING:
    from bl2.Engine import Weapon
    from bl2.WillowGame import WillowWeapon

reload_fix_option = BoolOption(
    "Fix Zero Ammo",
    True,  # noqa: FBT003
    description="Fixes weapons getting suck at 0 ammo and being unable to fire.",
)
swap_fix_option = BoolOption(
    "Fix Swap Start Fire",
    True,  # noqa: FBT003
    description="Fixes weapons not automatically starting to fire if you swap while holding fire.",
)


@cached_property
def begin_fire_super() -> UObject:
    return find_object("Function", "Engine.Weapon.Active.BeginFire")


@hook("WillowGame.WillowWeapon:Active.BeginFire")
def begin_fire(obj: WillowWeapon, args: WrappedStruct, *_: Any) -> None:
    if not reload_fix_option.value:
        return None
    super_func = BoundFunction(find_object("Function", "Engine.Weapon.Active.BeginFire"), obj)
    if args.FireModeNum == 1:
        super_func(args.FireModeNum)
        return Block
    if not obj.HasAmmo(args.FireModeNum):
        if obj.HasSpareAmmo():
            obj.StartReload(args.FireModeNum)
        else:
            obj.PlayDryFireSound(True)  # noqa: FBT003
        return Block
    if (
        obj.WorldInfo.TimeSeconds > obj.LastAutomaticBurstTime
        and not obj.bIsBlockedAfterBusy
        and not obj.bBurstDelayActive
    ) or obj.bBurstDelayActive:
        super_func(args.FireModeNum)
    return Block


@hook("WillowGame.WillowWeapon:WeaponEquipping.WeaponEquipped", immediately_enable=True)
def weapon_equipped(obj: UObject, *_: Any) -> None:
    if not swap_fix_option.value:
        return
    if not obj.Instigator.Class._inherits(find_class("WillowPlayerPawn")):
        return
    if obj.Instigator.Controller is None:
        return
    player_input = obj.Instigator.Controller.PlayerInput
    key = player_input.GetKeyForAction("Fire")
    for button in player_input.Buttons:
        if button.ButtonName == key and button.State in [
            BUTTON_STATE_Held,
            BUTTON_STATE_Pressed,
        ]:
            obj.SetPendingFire(0)
            break
    return


build_mod()
