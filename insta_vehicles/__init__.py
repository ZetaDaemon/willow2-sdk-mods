from __future__ import annotations

from typing import TYPE_CHECKING, Any

import unrealsdk
from mods_base import BoolOption, GroupedOption, SpinnerOption, build_mod, get_pc, hook, keybind
from unrealsdk.hooks import Block, Type

from insta_vehicles.ucaching import ObjReferenceByName

if TYPE_CHECKING:
    from bl2.Core import Object  # pyright: ignore[reportMissingModuleSource]
    from bl2.WillowGame import (
        CustomizationDefinition,  # pyright: ignore[reportMissingModuleSource]
        MissionObjectiveDefinition,  # pyright: ignore[reportMissingModuleSource]
        MissionTracker,  # pyright: ignore[reportMissingModuleSource]
        VehicleSpawnStationGFxDefinition,  # pyright: ignore[reportMissingModuleSource]
        VSSUIDefinition,  # pyright: ignore[reportMissingModuleSource]
        WillowGlobals,  # pyright: ignore[reportMissingModuleSource]
        WillowPlayerController,  # pyright: ignore[reportMissingModuleSource]
    )

    EInputEvent = Object.EInputEvent
else:
    EInputEvent = unrealsdk.find_enum("EInputEvent")

VEHICLE_SLOT = 0

# Const names for vehicles
## Base Game
RUNNER = "Runner"
TECHNICAL = "Technical"
ROCKET_RUNNER = "Rocket Runner"
MG_RUNNER = "Machine Gun Runner"
CATAPULT_TECHNICAL = "Catapult Technical"
SAWBLADE_TECHNICAL = "Sawblade Technical"

## Orchid
HARPOON_HOVERCRAFT = "Harpoon Hovercraft"
ROCKET_HOVERCRAFT = "Rocket Hovercraft"
SAWBLADE_HOVERCRAFT = "SawBlade Hovercraft"

## Sage
CORROSIVE_FANBOAT = "Corrosive Fan Boat"
INCENDIARY_FANBOAT = "Incendiary Fan Boat"
SHOCK_FANBOAT = "Shock Fan Boat"

VSSUIDEFS: dict[str, ObjReferenceByName[VSSUIDefinition]] = {
    ROCKET_RUNNER: ObjReferenceByName(
        "VSSUIDefinition", "GD_Globals.VehicleSpawnStation.VSSUI_RocketRunner"
    ),
    MG_RUNNER: ObjReferenceByName(
        "VSSUIDefinition", "GD_Globals.VehicleSpawnStation.VSSUI_MGRunner"
    ),
    CATAPULT_TECHNICAL: ObjReferenceByName(
        "VSSUIDefinition", "GD_Globals.VehicleSpawnStation.VSSUI_CatapultTechnical"
    ),
    SAWBLADE_TECHNICAL: ObjReferenceByName(
        "VSSUIDefinition", "GD_Globals.VehicleSpawnStation.VSSUI_SawBladeTechnical"
    ),
    HARPOON_HOVERCRAFT: ObjReferenceByName(
        "VSSUIDefinition", "GD_OrchidPackageDef.Vehicles.VSSUI_HarpoonHovercraft"
    ),
    ROCKET_HOVERCRAFT: ObjReferenceByName(
        "VSSUIDefinition", "GD_OrchidPackageDef.Vehicles.VSSUI_RocketHovercraft"
    ),
    SAWBLADE_HOVERCRAFT: ObjReferenceByName(
        "VSSUIDefinition", "GD_OrchidPackageDef.Vehicles.VSSUI_SawBladeHovercraft"
    ),
    CORROSIVE_FANBOAT: ObjReferenceByName(
        "VSSUIDefinition", "GD_SagePackageDef.Vehicles.VSSUI_CorrosiveFanBoat"
    ),
    INCENDIARY_FANBOAT: ObjReferenceByName(
        "VSSUIDefinition", "GD_SagePackageDef.Vehicles.VSSUI_IncendiaryFanBoat"
    ),
    SHOCK_FANBOAT: ObjReferenceByName(
        "VSSUIDefinition", "GD_SagePackageDef.Vehicles.VSSUI_ShockFanBoat"
    ),
}

RUNNER_OBJECTIVE: ObjReferenceByName[MissionObjectiveDefinition] = ObjReferenceByName(
    "MissionObjectiveDefinition", "GD_Episode03.M_Ep3_CatchARide:InstallNetworkInterfaceModule"
)
TECHNICAL_OBJECTIVE: ObjReferenceByName[MissionObjectiveDefinition] = ObjReferenceByName(
    "MissionObjectiveDefinition", "GD_Episode06.M_Ep6_RescueRoland:HelpBuildCar"
)
HOVERCRAFT_OBJECTIVE: ObjReferenceByName[MissionObjectiveDefinition] = ObjReferenceByName(
    "MissionObjectiveDefinition", "GD_Orchid_Plot_Mission02.M_Orchid_PlotMission02:ScanSkiff"
)
FANBOAT_OBJECTIVE: ObjReferenceByName[MissionObjectiveDefinition] = ObjReferenceByName(
    "MissionObjectiveDefinition", "GD_Sage_Ep1.M_Sage_Mission01:DefendRepair"
)

despawn_on_exit = BoolOption("Despawn on exit", False)
skip_animations = BoolOption(
    "Skip Animations", False, description="Skip the enter and exit animations"
)
prefer_technical = BoolOption("Prefer Technical", False)
runner_option = SpinnerOption("Runner", MG_RUNNER, [MG_RUNNER, ROCKET_RUNNER])
technical_option = SpinnerOption(
    "Technical", SAWBLADE_TECHNICAL, [SAWBLADE_TECHNICAL, CATAPULT_TECHNICAL]
)
hovercraft_option = SpinnerOption(
    "Hovercraft", HARPOON_HOVERCRAFT, [HARPOON_HOVERCRAFT, ROCKET_HOVERCRAFT, SAWBLADE_HOVERCRAFT]
)
fanboat_option = SpinnerOption(
    "Fan Boat", SHOCK_FANBOAT, [CORROSIVE_FANBOAT, INCENDIARY_FANBOAT, SHOCK_FANBOAT]
)

vehicle_choices_group = GroupedOption(
    "Vehicle Choices",
    [prefer_technical, runner_option, technical_option, hovercraft_option, fanboat_option],
)


def find_spawn_station_def() -> VehicleSpawnStationGFxDefinition | None:
    for stationdef in unrealsdk.find_all("VehicleSpawnStationGFxDefinition"):
        if stationdef == stationdef.Class.ClassDefaultObject:
            continue
        if len(stationdef.SupportedTags) == 0:
            continue
        return stationdef
    return None


def get_customisation_for_vehicle_def(
    vehicle_def: VSSUIDefinition,
) -> CustomizationDefinition | None:
    pc: WillowPlayerController = get_pc()
    for customisation in pc.ChosenVehicleCustomizations:
        if vehicle_def.VehicleFamily == customisation.FamilyDef:
            return customisation.CustomizationDef[VEHICLE_SLOT]
    return None


def station_supports_vehicle(
    station_def: VehicleSpawnStationGFxDefinition, vehicle_def: VSSUIDefinition
) -> bool:
    return set(vehicle_def.RequiredTags).issubset(
        list(station_def.SupportedTags) + list(station_def.RequiredTags)
    )


def lookup_vehicle_def(vehicle_name: str) -> VSSUIDefinition | None:
    if (vehicle_ref := VSSUIDEFS.get(vehicle_name)) is not None and (
        vehicle_def := vehicle_ref()
    ) is not None:
        return vehicle_def
    return None


def has_completed_objective(objective_ref: ObjReferenceByName[MissionObjectiveDefinition]) -> bool:
    pc: WillowPlayerController = get_pc()
    mission_tracker: MissionTracker = pc.WorldInfo.GRI.MissionTracker
    return (objective := objective_ref()) and mission_tracker.IsObjectiveBitSet(
        objective, objective.ObjectiveCount
    )


def get_vehicle_def(station: VehicleSpawnStationGFxDefinition) -> VSSUIDefinition | None:
    if (
        (
            has_completed_objective(TECHNICAL_OBJECTIVE)
            and prefer_technical.value
            and (vehicle_def := lookup_vehicle_def(technical_option.value))
            and station_supports_vehicle(station, vehicle_def)
        )
        or (
            has_completed_objective(RUNNER_OBJECTIVE)
            and (vehicle_def := lookup_vehicle_def(runner_option.value))
            and station_supports_vehicle(station, vehicle_def)
        )
        or (
            has_completed_objective(HOVERCRAFT_OBJECTIVE)
            and (vehicle_def := lookup_vehicle_def(hovercraft_option.value))
            and station_supports_vehicle(station, vehicle_def)
        )
        or (
            has_completed_objective(FANBOAT_OBJECTIVE)
            and (vehicle_def := lookup_vehicle_def(fanboat_option.value))
            and station_supports_vehicle(station, vehicle_def)
        )
    ):
        return vehicle_def
    return None


WILLOW_GLOBALS_CLASS_DEFAULT: WillowGlobals = unrealsdk.find_class(
    "WillowGlobals"
).ClassDefaultObject


@keybind("Summon Vehicle", event_filter=EInputEvent.IE_Pressed)
def summon_vehicle() -> None:
    pc: WillowPlayerController = get_pc()
    willow_globals = WILLOW_GLOBALS_CLASS_DEFAULT.GetWillowGlobals()
    pop_master = willow_globals.GetPopulationMaster()
    using_vehicle, vehicle = pc.IsUsingVehicleEx(True, None)

    if using_vehicle:
        vehicle.DriverLeave(skip_animations.value)
        if despawn_on_exit.value:
            pop_master.DespawnVehicleFromVehicleSpawnStation(VEHICLE_SLOT)
        return

    if (stationdef := find_spawn_station_def()) is None:
        return

    vehicle_def = get_vehicle_def(stationdef)
    data_manager = willow_globals.GetPlayerPawnDataManager()
    spawn_def = data_manager.LoadVSSVehicleDefinition(vehicle_def.PathToVSSDefinition, pc)
    if pop_master.GetVehicleFromVehicleSpawnStation(VEHICLE_SLOT) is not None:
        pop_master.DespawnVehicleFromVehicleSpawnStation(VEHICLE_SLOT)
    pop_master.SpawnVehicleFromVehicleSpawnStation(
        VEHICLE_SLOT, spawn_def, pc.Pawn.Location, pc.Pawn.Rotation
    )
    if (vehicle := pop_master.GetVehicleFromVehicleSpawnStation(VEHICLE_SLOT)) is None:
        return
    vehicle.InitiateCustomizationRequest(get_customisation_for_vehicle_def(vehicle_def))
    vehicle.TryToRide(pc.Pawn, skip_animations.value)


@hook("WillowGame.WillowPlayerController:ExitVehicle")
def exit_vehicle(pc: WillowPlayerController, *_: Any) -> type[Block]:
    using_vehicle, vehicle = pc.IsUsingVehicleEx(True, None)
    if not using_vehicle:
        return Block
    vehicle.DriverLeave(skip_animations.value)

    willow_globals = WILLOW_GLOBALS_CLASS_DEFAULT.GetWillowGlobals()
    pop_master = willow_globals.GetPopulationMaster()
    if despawn_on_exit.value:
        pop_master.DespawnVehicleFromVehicleSpawnStation(VEHICLE_SLOT)

    return Block


build_mod(options=[despawn_on_exit, skip_animations, vehicle_choices_group])
