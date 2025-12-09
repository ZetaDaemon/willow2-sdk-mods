from mods_base import build_mod, hook, BoolOption
from unrealsdk.unreal import UObject, BoundFunction, WrappedStruct
from unrealsdk.hooks import Block
from unrealsdk import find_object, find_class
from typing import Any

BUTTON_STATE_Pressed = 0
BUTTON_STATE_Held = 1


reload_fix_option = BoolOption(
    "Fix Zero Ammo",
    True,
    description="Fixes weapons getting suck at 0 ammo and being unable to fire.",
)
swap_fix_option = BoolOption(
    "Fix Swap Start Fire",
    True,
    description="Fixes weapons not automatically starting to fire if you swap while holding fire.",
)


@hook("WillowGame.WillowWeapon:Active.BeginFire")
def begin_fire(obj: UObject, args: WrappedStruct, *_: Any) -> None:
    if not reload_fix_option.value:
        return
    super_func = BoundFunction(
        find_object("Function", "Engine.Weapon.Active.BeginFire"), obj
    )
    if args.FireModeNum == 1:
        super_func(args.FireModeNum)
        return Block
    if not obj.HasAmmo(args.FireModeNum):
        if obj.HasSpareAmmo():
            obj.StartReload(args.FireModeNum)
        else:
            obj.PlayDryFireSound(True)
        return Block
    if (
        obj.WorldInfo.TimeSeconds > obj.LastAutomaticBurstTime
        and not obj.bIsBlockedAfterBusy
        and not obj.bBurstDelayActive
        or obj.bBurstDelayActive
    ):
        super_func(args.FireModeNum)
    return Block


@hook("WillowGame.WillowWeapon:WeaponEquipping.WeaponEquipped", immediately_enable=True)
def weapon_equipped(obj: UObject, args: WrappedStruct, *_: Any) -> None:
    if not swap_fix_option.value:
        return
    if not obj.Instigator.Class._inherits(find_class("WillowPlayerPawn")):
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
