from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

import unrealsdk
from mods_base import hook
from unrealsdk import logging
from unrealsdk.hooks import Block, Type

from .inventory_tools import (
    clear_pending_warning,
    collect_bank_codes,
    collect_item_codes,
    collect_weapon_codes,
    is_pending_warning,
    remove_backed_up_bank_codes,
    remove_backed_up_inv_codes,
    restore_bank_codes,
    restore_item_codes,
    restore_weapon_codes,
)
from .item_codes import ItemCodeDecodeError, get_item_code
from .sanity_saver_importer import find_sanity_saver_saves, import_bank, import_inventory
from .saves import PlayerSaveData, load_player_save, save_player_save
from .settings import (
    IGNORE_LOAD_WARNING,
    PROTECT_ITEMS,
    REFRESH_VENDORS,
    REMOVE_MODDED_GROUND_ITEMS,
)
from .ui import LOAD_WARNING_BOX

if TYPE_CHECKING:
    from bl2.Engine import Actor, WillowInventoryDefinition
    from bl2.WillowGame import (
        PlayerSaveGame,
        WillowInventoryManager,
        WillowInventoryStorage,
        WillowItemTypes,
        WillowPickup,
        WillowPlayerController,
        WillowVendingMachine,
        WillowWeaponTypes,
    )
    from unrealsdk.unreal import BoundFunction, WrappedStruct

    ItemDefinitionData = WillowItemTypes.ItemDefinitionData
    WeaponDefinitionData = WillowWeaponTypes.WeaponDefinitionData
    DefinitionData = ItemDefinitionData | WeaponDefinitionData

    WeaponSaveGameData = PlayerSaveGame.WeaponSaveGameData
    InventorySaveGameData = PlayerSaveGame.InventorySaveGameData

    EPlayerDroppability = WillowInventoryDefinition.EPlayerDroppability
    ENetRole = Actor.ENetRole
else:
    EPlayerDroppability = unrealsdk.find_enum("EPlayerDroppability")
    ENetRole = unrealsdk.find_enum("ENetRole")


WILLOW_INVENTORY_MANGER_CLASS = unrealsdk.find_class("WillowInventoryManager")


@hook("WillowGame.WillowInventoryStorage:Close")  # pyright: ignore[reportArgumentType]
def close_bank(
    obj: WillowInventoryStorage, _args: WrappedStruct, _ret: Any, _func: BoundFunction
) -> None:
    if not obj.ChestIsOpen:
        return

    outer = cast("WillowInventoryManager | None", obj.Outer)

    if outer is None or not outer.Class._inherits(WILLOW_INVENTORY_MANGER_CLASS):
        return

    if obj != outer.TheBank:
        return

    owner = cast("WillowPlayerController | None", outer.GetOwningPlayerController())
    if owner is None:
        return

    save_data = load_player_save(owner.SaveGameFileId)
    save_data["bank"] = collect_bank_codes(obj)
    remove_backed_up_bank_codes(save_data)
    save_player_save(owner.SaveGameFileId, save_data)


@hook("WillowGame.WillowPlayerController:GeneratePlayerSaveGame")  # pyright: ignore[reportArgumentType]
def generate_save(
    obj: WillowPlayerController, _args: WrappedStruct, _ret: Any, _func: BoundFunction
) -> None:
    inv_manager = obj.GetPawnInventoryManager()
    if inv_manager is None:
        return

    previous = load_player_save(obj.SaveGameFileId)
    save_data: PlayerSaveData = {
        "weapons": collect_weapon_codes(inv_manager),
        "items": collect_item_codes(obj, inv_manager),
        "bank": previous["bank"],
        "backup": previous["backup"],
    }

    remove_backed_up_inv_codes(save_data)

    save_player_save(obj.SaveGameFileId, save_data)


@hook("WillowGame.WillowPlayerController:LoadPlayerSaveGame")  # pyright: ignore[reportArgumentType]
def load_save(
    obj: WillowPlayerController,
    args: WillowPlayerController.LoadPlayerSaveGame.args,
    _ret: Any,
    _func: BoundFunction,
) -> None:
    if not obj.IsLocalPlayerController():
        return

    save = args.NewSaveGame
    if save is None or save.SaveGameId < 0:
        return

    save_data = load_player_save(save.SaveGameId)

    try:
        ss_path = find_sanity_saver_saves()
        if ss_path is not None:
            import_inventory(save, save_data, ss_path)
    except (ValueError, OSError, EOFError) as exc:
        logging.error(f"Sanity Saver import failed: {exc}")

    restore_weapon_codes(save, save_data)
    restore_item_codes(save, save_data)
    save_player_save(save.SaveGameId, save_data)


@hook("WillowGame.WillowInventoryStorage:Open", Type.POST)  # pyright: ignore[reportArgumentType]
def open_bank(
    obj: WillowInventoryStorage,
    _args: WrappedStruct,
    ret: WillowInventoryStorage.Open.ret,
    _func: BoundFunction,
) -> None:
    if not obj.ChestIsOpen or not ret:
        return

    outer = cast("WillowInventoryManager | None", obj.Outer)

    if outer is None or not outer.Class._inherits(WILLOW_INVENTORY_MANGER_CLASS):
        return

    if obj != outer.TheBank:
        return

    owner = cast("WillowPlayerController | None", outer.GetOwningPlayerController())
    if owner is None or not owner.IsLocalPlayerController():
        return

    save_data = load_player_save(owner.SaveGameFileId)

    try:
        ss_path = find_sanity_saver_saves()
        if ss_path is not None:
            import_bank(obj, owner.SaveGameFileId, save_data, ss_path)
    except (ValueError, OSError, EOFError) as exc:
        logging.error(f"Sanity Saver import failed: {exc}")

    restore_bank_codes(obj, save_data)
    save_player_save(owner.SaveGameFileId, save_data)


@hook("WillowGame.WillowPlayerController:ValidateItemDefinition")
@hook("WillowGame.WillowPlayerController:ValidateWeaponDefinition")
def validate_definition(*_: Any) -> tuple[type[Block], bool]:
    return Block, True


@hook("WillowGame.WillowVendingMachine:SetFeaturedItem")  # pyright: ignore[reportArgumentType]
def refresh_vendor(
    obj: WillowVendingMachine, _args: WrappedStruct, _ret: Any, _func: BoundFunction
) -> type[Block] | None:

    if not REFRESH_VENDORS.value:
        return None
    if obj.Role != ENetRole.ROLE_Authority:
        return None

    refresh_vendor.disable()
    try:
        obj.ResetInventory()
    finally:
        refresh_vendor.enable()

    return Block


@hook("WillowGame.WillowPlayerController:LoadPlayerSaveGame", Type.POST)  # pyright: ignore[reportArgumentType]
def post_load_save(
    obj: WillowPlayerController,
    _args: WillowPlayerController.LoadPlayerSaveGame.args,
    _ret: Any,
    _func: BoundFunction,
) -> None:
    if not obj.IsLocalPlayerController() or not is_pending_warning():
        return
    if not PROTECT_ITEMS.value or IGNORE_LOAD_WARNING.value:
        return
    LOAD_WARNING_BOX.show()
    clear_pending_warning()


@hook("WillowGame.WillowPickup:ShouldSaveInPopulationSystem")  # pyright: ignore[reportArgumentType]
def skip_unserializable_pickup(
    obj: WillowPickup, _args: WrappedStruct, _ret: Any, _func: BoundFunction
) -> tuple[type[Block], bool] | None:
    if not REMOVE_MODDED_GROUND_ITEMS.value or not obj.bCanBeSavedAcrossLevelTransition:
        return None

    item = obj.Inventory
    try:
        if item is not None and get_item_code(item) is not None:
            return Block, False
    except ItemCodeDecodeError as exc:
        unrealsdk.logging.error(f"Could not check ground pickup for serialization: {exc}")

    return None
