from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import TYPE_CHECKING, Any, cast

import unrealsdk
from mods_base import build_mod, get_pc, hook, keybind
from mods_base.options import BoolOption, GroupedOption, SliderOption, SpinnerOption
from unrealsdk.hooks import Block, Type
from unrealsdk.unreal import WeakPointer

from better_third_person import uemath

if TYPE_CHECKING:
    from bl2.Core import Object
    from bl2.Engine import AttributeDefinition
    from bl2.WillowGame import WillowPlayerController, WillowWeapon

    EZoomState = WillowWeapon.EZoomState
    Vector = Object.Vector
    Rotator = Object.Rotator
else:
    EZoomState = unrealsdk.find_enum("EZoomState")

type PreHookRet = tuple[type[Block], Any] | type[Block] | None


class AimZoomMode(StrEnum):
    """Aim mode possibilities."""

    ZOOM = "Zoom"
    SCOPE = "Scope"
    DOUBLE_CLICK = "Double Click"


@dataclass
class ScaledSlider(SliderOption):
    """Slider option that allows for getting a scaled version of the value."""

    scale: float = 1

    @property
    def scaled_value(self) -> float:
        """Access value with scaling.

        Allows the internal value which is displayed in the menus to have a different scale
        to the value used.
        """
        return self.value * self.scale

    @scaled_value.setter
    def scaled_value(self, value: float) -> None:
        value /= self.scale
        if self.is_integer:
            value = round(value)
        self.value = value


camera_scale = ScaledSlider("Camera Distance", 30, 0, 100, scale=0.1)
horizontal_offset = ScaledSlider("Horizontal Offset", 15, -100, 100, scale=0.1)
vertical_offset = ScaledSlider("Vertical Offset", 10, -100, 100, scale=0.1)

third_person_camera_settings = GroupedOption(
    "Camera Settings", [camera_scale, horizontal_offset, vertical_offset]
)

aim_mode = SpinnerOption("Aim Mode", AimZoomMode.ZOOM, list(AimZoomMode), True)

default_third_person = BoolOption(
    "Default Third Person", False, description="Should third person be used by default."
)

zoom_fov_modifier = ScaledSlider(
    "Zoom FOV Modifier",
    0,
    -100,
    0,
    scale=0.01,
    description="Reduce the aim fov modifier while in zoom mode.",
)

use_aim_fix = BoolOption("Use Aim Fix", True, description="Fix third person weapon aim.")

should_resume_third_person = False
should_stop_third_person = False


def start_third_person(pc: WillowPlayerController) -> None:
    view_target = pc.Pawn
    view_target.CameraScale = camera_scale.scaled_value
    view_target.CameraScaleRight = horizontal_offset.scaled_value
    view_target.CameraScaleUp = vertical_offset.scaled_value
    pc.SetBehindView(True)


def stop_third_person(pc: WillowPlayerController) -> None:
    pc.SetBehindView(False)


def toggle_third_person() -> None:
    pc = cast("WillowPlayerController", get_pc())
    if pc.bBehindView:
        stop_third_person(pc)
    else:
        start_third_person(pc)


modifier_pointer: WeakPointer = WeakPointer()


def apply_fov_modifier(weapon: WillowWeapon) -> None:
    if weapon is None:
        return

    attr = cast(
        "AttributeDefinition",
        unrealsdk.find_object("AttributeDefinition", "D_Attributes.Weapon.WeaponZoomEndFOV"),
    )
    if attr is None:
        return

    zoom_end_fov = weapon.ZoomedEndFOVBaseValue
    value = -1 * (70 - zoom_end_fov) * zoom_fov_modifier.scaled_value
    if value == 0:
        return

    if (modifier := modifier_pointer()) is None:
        modifier = unrealsdk.construct_object("AttributeModifier", weapon)
    else:
        attr.RemoveAttributeModifier(weapon, modifier)  # ty: ignore[invalid-argument-type]
    modifier.Type = 1
    modifier.Value = value
    attr.AddAttributeModifier(weapon, modifier)  # ty: ignore[invalid-argument-type]
    modifier_pointer.replace(modifier)


def remove_fov_modifier(weapon: WillowWeapon) -> None:
    if weapon is None:
        return
    attr = cast(
        "AttributeDefinition",
        unrealsdk.find_object("AttributeDefinition", "D_Attributes.Weapon.WeaponZoomEndFOV"),
    )
    if attr is None:
        return

    if (modifier := modifier_pointer()) is not None:
        attr.RemoveAttributeModifier(weapon, modifier)  # ty: ignore[invalid-argument-type]


@keybind("Toggle Third Person")
def toggle_third_person_callback() -> None:
    toggle_third_person()


@hook("WillowGame.WillowPlayerController:Possess", Type.POST)
def pc_possess(pc: WillowPlayerController, *_: Any) -> None:
    if default_third_person.value:
        start_third_person(pc)


@hook("WillowGame.WillowPlayerController:StartAltFire")
def pc_start_alt_fire(pc: WillowPlayerController, *_: Any) -> PreHookRet:
    global should_resume_third_person, should_stop_third_person
    if (pawn := pc.pawn) is not None and pawn.OffHandWeapon is not None:
        pc.StartFire(1)
        return Block
    hud = pc.GetHUDMovie()
    if (pc.WorldInfo.TimeSeconds - pc.LastZoomTime) < pc.PlayerInput.DoubleClickTime:
        if pc.bBehindView and aim_mode.value == AimZoomMode.DOUBLE_CLICK:
            if pawn.Weapon.ZoomState == EZoomState.ZST_Zoomed:
                should_resume_third_person = True
                stop_third_person(pc)
                remove_fov_modifier(pawn.Weapon)
                hud.CrosshairWidget.bScopeCrosshair = False
                pawn.Weapon.DisplayScope(True)
            else:
                should_stop_third_person = True
            if not pc.bZoomToggle:
                pc.StartFire(1)
            return Block
    elif pc.bZoomToggle and pc.isZoomed():
        if should_resume_third_person:
            start_third_person(pc)
            should_resume_third_person = False
        pc.StopFire(1)
        return Block
    pc.StartFire(1)
    pc.LastZoomTime = pc.WorldInfo.TimeSeconds
    if pc.bBehindView and aim_mode.value == AimZoomMode.SCOPE:
        should_stop_third_person = True
    return Block


@hook("WillowGame.WillowPlayerController:StopAltFire")
def pc_stop_alt_fire(pc: WillowPlayerController, *_: Any) -> PreHookRet:
    global should_resume_third_person
    if should_resume_third_person and not pc.bZoomToggle:
        start_third_person(pc)
        should_resume_third_person = False


@hook("WillowGame.WillowWeapon:DisplayScope")  # ty: ignore[invalid-argument-type]
def is_scoped(weapon: WillowWeapon, args: WillowWeapon.DisplayScope.args, *_: Any) -> PreHookRet:
    if not args.bDisplay:
        return None
    if (instigator := weapon.Instigator) is None or instigator.Class.Name != "WillowPlayerPawn":
        return None
    if instigator.Controller.bBehindView:
        return Block
    return None


@hook("WillowGame.WillowWeapon:SetZoomState")  # ty: ignore[invalid-argument-type]
def set_zoom_state(
    weapon: WillowWeapon, args: WillowWeapon.SetZoomState.args, *_: Any
) -> PreHookRet:
    global should_stop_third_person, should_resume_third_person
    if (owner := weapon.Owner) is None or (controller := owner.Controller) != get_pc():
        return

    hud = controller.GetHUDMovie()
    match args.NewZoomState:
        case EZoomState.ZST_Zoomed:
            if should_stop_third_person:
                stop_third_person(owner.Controller)
                remove_fov_modifier(weapon)
                weapon.ZoomedFOV = weapon.ZoomedEndFOV
                should_stop_third_person = False
                should_resume_third_person = True
            elif controller.bBehindView:
                hud.CrosshairWidget.bScopeCrosshair = True

        case EZoomState.ZST_ZoomingIn:
            if controller.bBehindView:
                apply_fov_modifier(weapon)

        case EZoomState.ZST_ZoomingOut:
            hud.CrosshairWidget.bScopeCrosshair = False

        case EZoomState.ZST_NotZoomed:
            remove_fov_modifier(weapon)
    return


@hook("WillowGame.WillowPlayerController:Get3rdPersonAimRotation")  # ty: ignore[invalid-argument-type]
def get_adjusted_aim(
    pc: WillowPlayerController, args: WillowPlayerController.Get3rdPersonAimRotation.args, *_: Any
) -> PreHookRet:
    if not use_aim_fix.value:
        return None
    if (weapon := args.W) is None:
        return None
    pawn = pc.MyWillowPawn
    base_aim_loc = uemath.Vector(pawn.Cached3rdPersonCamLoc)
    base_aim_rot = uemath.Rotator(pawn.Cached3rdPersonCamRot)
    base_aim_vec = uemath.Vector(base_aim_rot)
    base_aim_end = base_aim_loc + (base_aim_vec * weapon.WeaponRange)
    impact, __ = weapon.CalcWeaponFire(base_aim_loc.wrapped_struct, base_aim_end.wrapped_struct)
    return Block, uemath.Rotator(
        uemath.Vector(impact.HitLocation) - uemath.Vector(args.StartFireLoc)
    ).wrapped_struct


build_mod(
    options=[
        default_third_person,
        aim_mode,
        zoom_fov_modifier,
        use_aim_fix,
        third_person_camera_settings,
    ]
)
