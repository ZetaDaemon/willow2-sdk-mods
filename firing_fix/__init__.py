from mods_base import build_mod, hook
from unrealsdk.unreal import UObject, BoundFunction, WrappedStruct
from unrealsdk.hooks import Block
from unrealsdk import find_object
from typing import Any


@hook("WillowGame.WillowWeapon:Active.BeginFire")
def active_begin_fire(obj: UObject, args: WrappedStruct, *_: Any) -> None:
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


build_mod()
