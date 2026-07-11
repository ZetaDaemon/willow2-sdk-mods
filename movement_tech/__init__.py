from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any, cast

import uemath
import unrealsdk
from mods_base import (
    BoolOption,
    NestedOption,
    SliderOption,
    ValueOption,
    build_mod,
    get_pc,
    hook,
    keybind,
)
from networking import add_network_functions, host
from unrealsdk.hooks import Block, Type
from unrealsdk.unreal import WeakPointer

from movement_tech.ucaching import ObjReferenceByName

if TYPE_CHECKING:
    from bl2.Core import Object  # pyright: ignore[reportMissingModuleSource]
    from bl2.Engine import Actor, BehaviorBase  # pyright: ignore[reportMissingModuleSource]
    from bl2.WillowGame import (
        Behavior_FireBeam,  # pyright: ignore[reportMissingModuleSource]
        ProjectileDefinition,  # pyright: ignore[reportMissingModuleSource]
        SpecialMove_WeaponAction,  # pyright: ignore[reportMissingModuleSource]
        WillowPlayerController,  # pyright: ignore[reportMissingModuleSource]
        WillowPlayerPawn,  # pyright: ignore[reportMissingModuleSource]
        WillowPlayerReplicationInfo,  # pyright: ignore[reportMissingModuleSource]
        WillowProjectile,  # pyright: ignore[reportMissingModuleSource]
    )

    EPhysics = Actor.EPhysics
    EInputEvent = Object.EInputEvent
    EBehaviorContext = BehaviorBase.EBehaviorContext

else:
    EPhysics = unrealsdk.find_enum("EPhysics")
    EInputEvent = unrealsdk.find_enum("EInputEvent")
    EBehaviorContext = unrealsdk.find_enum("EBehaviorContext")


@dataclass
class PlayerInfo:
    """Store movement tech info for players."""

    can_double_jump: bool = True
    grapple_projectile: WeakPointer[WillowProjectile] | None = None
    grapple_duration_remaining: float = 0


def get_value_in_cm(option: ValueOption[float]) -> float:
    return option.value * 100


COMMANDS_FILE_NAME = "commands.txt"
COMMANDS_FILE_PATH = (Path(__file__).parent / COMMANDS_FILE_NAME).relative_to(
    Path(sys.executable).parent.parent, walk_up=True
)

PLAYERS: dict[int, PlayerInfo] = {}


DOUBLEJUMP_ENABLED = BoolOption("Double Jump Enabled", True)

SLAM_ENABLED = BoolOption("Slam Enabled", True)
SLAM_Z_VELOCITY = SliderOption(
    "Slam Speed", -2000, -10000, -500, -500, description="The speed in m/s d to slam. Default -20"
)
SLAM_OPTIONS = NestedOption("Slam Configuration", [SLAM_Z_VELOCITY])


GRAPPLE_ENABLED = BoolOption("Grapple Enabled", True)
GRAPPLE_PROJECTILE_SPEED = SliderOption(
    "Grapple Hook Speed",
    200,
    50,
    500,
    50,
    description="The speed in m/s d of the grappling hook thrown out. Default 200",
)
GRAPPLE_PULL_STRENGTH = SliderOption(
    "Grapple Pull Strength",
    20,
    5,
    50,
    5,
    description="The speed  in m/s you're pulled towards where the grapple landed. Default 20",
)
GRAPPLE_DURATION = SliderOption(
    "Grapple Duration",
    3,
    1,
    10,
    description="The amount of seconds before the grapple automatically ends. Default 3",
)
GRAPPLE_MIN_DISTANCE = SliderOption(
    "Grapple Min Distance",
    3,
    1,
    10,
    1,
    description="Distance in meters where the grapple stops. Default 5",
)
GRAPPLE_MAX_DISTANCE = SliderOption(
    "Grapple Max Distance",
    60,
    10,
    100,
    10,
    description="Distance in meters for the maximum grapple range. Default 60",
)
GRAPPLE_OPTIONS = NestedOption(
    "Grapple Configuration",
    [
        GRAPPLE_PROJECTILE_SPEED,
        GRAPPLE_PULL_STRENGTH,
        GRAPPLE_DURATION,
        GRAPPLE_MIN_DISTANCE,
        GRAPPLE_MAX_DISTANCE,
    ],
)


PACKAGE_NAME = "Z_MOVEMENT_TECH_PKG"
FIRE_BEAM: ObjReferenceByName[Behavior_FireBeam] = ObjReferenceByName(
    "Behavior_FireBeam", f"{PACKAGE_NAME}.FireGrappleBeam"
)
PROJEECTILE_DEF: ObjReferenceByName[ProjectileDefinition] = ObjReferenceByName(
    "ProjectileDefinition", f"{PACKAGE_NAME}.GrappleProjectile"
)
SPECIAL_MOVE: ObjReferenceByName[SpecialMove_WeaponAction] = ObjReferenceByName(
    "SpecialMove_WeaponAction", f"{PACKAGE_NAME}.ThrowGrenadeAnim"
)
SPECIAL_MOVE_1ST: ObjReferenceByName[SpecialMove_WeaponAction] = ObjReferenceByName(
    "SpecialMove_FirstPerson", f"{PACKAGE_NAME}.ThrowGrenadeAnim_1st"
)


def setup_objects() -> None:
    get_pc().ConsoleCommand(f"exec {COMMANDS_FILE_PATH!s}")


@hook("WillowGame.FrontendGFxMovie:Start", Type.POST_UNCONDITIONAL, immediately_enable=True)
def frontend_start(*_: Any) -> None:
    frontend_start.disable()
    if _mod_instance.is_enabled:
        setup_objects()


def on_enable() -> None:
    if frontend_start.get_active_count() > 0:
        return
    setup_objects()
    return


def lookup_player_info(pc: WillowPlayerController) -> PlayerInfo:
    player_id = pc.PlayerReplicationInfo.PlayerID
    if (info := PLAYERS.get(player_id)) is None:
        info = PlayerInfo()
        PLAYERS[player_id] = info
    return info


@hook("WillowGame.WillowPlayerPawn:CanJump")
def can_jump(
    player_pawn: WillowPlayerPawn,
    _2: WillowPlayerPawn._CanJump.args,
    _3: WillowPlayerPawn._CanJump.ret,
    func: WillowPlayerPawn._CanJump,
) -> tuple[type[Block], bool] | None:
    physics = player_pawn.Physics
    info = lookup_player_info(player_pawn.Controller)

    if physics != EPhysics.PHYS_Falling:
        return None
    if not info.can_double_jump:
        return None

    player_pawn.Physics = EPhysics.PHYS_Walking
    can_jump.disable()
    if func():
        player_pawn.Physics = physics
        info.can_double_jump = False
        can_jump.enable()
        return Block, True
    can_jump.enable()
    player_pawn.Physics = physics
    return None


@hook("WillowGame.WillowPlayerPawn:PlayLanded")
def play_landed(pawn: WillowPlayerPawn, *_: Any) -> None:
    info = lookup_player_info(pawn.Controller)
    info.can_double_jump = True


@host.message
def request_slam() -> None:
    pawn = cast(
        "WillowPlayerController", cast("WillowPlayerReplicationInfo", request_slam.sender).Owner
    ).Pawn
    if pawn.Physics != EPhysics.PHYS_Falling:
        return
    pawn.Velocity.Z += get_value_in_cm(SLAM_Z_VELOCITY)


@hook("WillowGame.WillowPlayerInput:DuckPressed")
def duck_pressed(*_: Any) -> None:
    request_slam()


@keybind("Grapple", event_filter=EInputEvent.IE_Pressed)
def try_grapple() -> None:
    pc: WillowPlayerController = get_pc()
    info = lookup_player_info(pc)
    if not pc.CanPerformWeaponAction():
        return
    if info.grapple_projectile is not None and info.grapple_projectile() is not None:
        return
    pawn = pc.Pawn
    pawn.SMComponent.PlayLocal(SPECIAL_MOVE(), 1)
    pc.PerformSharedWeaponActions(
        pawn.SMComponent.PlayLocal(SPECIAL_MOVE_1ST(), 1), "GrenadeThrowComplete"
    )
    pc.bThrowingGrenade = True


@hook("WillowGame.WillowPlayerController:Behavior_SpawnCurrentProjectile", Type.POST)
def spawn_projectile(
    pc: WillowPlayerController,
    args: WillowPlayerController._Behavior_SpawnCurrentProjectile.args,
    ret: WillowProjectile,
    *_: Any,
) -> None:
    if ret is None:
        return
    if args.CurrentProjectile != PROJEECTILE_DEF():
        return
    info = lookup_player_info(pc)

    pawn = pc.Pawn
    projectile = ret
    forward = uemath.Vector(pc.Rotation) * 50

    projectile.MaxSpeed = get_value_in_cm(GRAPPLE_PROJECTILE_SPEED)
    projectile.SetVelocityAndAcceleration((forward).normalize().to_ue_vector())
    info.grapple_projectile = WeakPointer(projectile)

    fire_beam = FIRE_BEAM()
    fire_beam.SourceOffset = unrealsdk.make_struct(
        "Vector",
        X=pawn.CylinderComponent.CollisionRadius * -0.8,
        Y=pawn.CylinderComponent.CollisionRadius * -0.5,
    )
    fire_beam.ApplyBehaviorToContext(
        pawn,
        unrealsdk.make_struct("BehaviorKernelInfo"),
        pawn,
        pawn,
        projectile,
        unrealsdk.make_struct("BehaviorParameters"),
    )
    info.grapple_duration_remaining += get_value_in_cm(GRAPPLE_DURATION)


@hook("WillowGame.WillowPlayerController:PlayerTick")
def player_tick(
    pc: WillowPlayerController, args: WillowPlayerController._PlayerTick.args, *_: Any
) -> None:
    pawn = pc.Pawn
    info = lookup_player_info(pc)
    if info.grapple_projectile is None or (projectile := info.grapple_projectile()) is None:
        return
    info.grapple_duration_remaining -= args.DeltaTime
    target_location = uemath.Vector(projectile.Location)
    location = uemath.Vector(pc.Pawn.Location)
    distance = abs(target_location.distance(location))
    if (
        info.grapple_duration_remaining <= 0
        or distance > get_value_in_cm(GRAPPLE_MAX_DISTANCE)
        or (projectile.MaxSpeed <= 0 and distance < get_value_in_cm(GRAPPLE_MIN_DISTANCE))
    ):
        pawn.CustomGravityScaling = 1
        info.grapple_projectile = None
        projectile_manager = pc.Pawn.GetLightProjMgrFor(None)
        projectile_manager.DeleteBeamsFor(projectile)
        projectile.Detonate()
        pawn.Velocity = (uemath.Vector(pawn.Velocity) / 5).to_ue_vector()
        return
    if projectile.MaxSpeed > 0:
        return
    target_location = uemath.Vector(projectile.Location)
    location = uemath.Vector(pc.Pawn.Location)
    direction = (target_location - location).normalize()
    pawn.CustomGravityScaling = 0
    if pawn.Physics == EPhysics.PHYS_Walking:
        pawn.Velocity.Z = pawn.JumpZ
        pawn.Physics = EPhysics.PHYS_Falling
    pawn.Velocity = (
        uemath.Vector(pawn.Velocity) + direction * get_value_in_cm(GRAPPLE_PULL_STRENGTH)
    ).to_ue_vector()
    return


_mod_instance = add_network_functions(
    build_mod(
        options=[DOUBLEJUMP_ENABLED, SLAM_ENABLED, GRAPPLE_ENABLED, SLAM_OPTIONS, GRAPPLE_OPTIONS]
    )
)
