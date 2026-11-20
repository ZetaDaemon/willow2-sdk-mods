from __future__ import annotations

from typing import TYPE_CHECKING, cast

import unrealsdk
from unrealsdk import logging

from .item_codes import (
    WILLOW_ITEM_CLASS,
    WILLOW_WEAPON_CLASS,
    ItemCodeDecodeError,
    decode_modded_item_code,
    get_item_code,
)
from .saves import InvItemSaveData, ItemSaveData, PlayerSaveData, PlayerSaveItems, WeaponSaveData
from .settings import PROTECT_ITEMS

if TYPE_CHECKING:
    from collections.abc import Callable

    from bl2.Engine import WillowInventoryDefinition
    from bl2.WillowGame import (
        PlayerSaveGame,
        WillowInventoryManager,
        WillowInventoryStorage,
        WillowItem,
        WillowItemTypes,
        WillowPlayerController,
        WillowWeapon,
        WillowWeaponTypes,
    )
    from unrealsdk.unreal import UClass

    ItemDefinitionData = WillowItemTypes.ItemDefinitionData
    WeaponDefinitionData = WillowWeaponTypes.WeaponDefinitionData
    DefinitionData = ItemDefinitionData | WeaponDefinitionData

    WeaponSaveGameData = PlayerSaveGame.WeaponSaveGameData
    InventorySaveGameData = PlayerSaveGame.InventorySaveGameData

    EPlayerDroppability = WillowInventoryDefinition.EPlayerDroppability
else:
    EPlayerDroppability = unrealsdk.find_enum("EPlayerDroppability")

pending_missing_parts_warning: bool = False


def clear_pending_warning() -> None:
    global pending_missing_parts_warning
    pending_missing_parts_warning = False


def is_pending_warning() -> bool:
    return pending_missing_parts_warning


def collect_weapon_codes(inv_manager: WillowInventoryManager) -> dict[str, WeaponSaveData]:
    weapons: dict[str, WeaponSaveData] = {}
    if inv_manager is None:
        return weapons  # pyright: ignore[reportUnreachable]

    _, weapon_list = inv_manager.GetWeaponList(
        [], True, True, EPlayerDroppability.EPD_CannotDropOrSell, True
    )

    for weapon in weapon_list:
        if weapon is None or not weapon.CanBeSaved():
            continue
        code = get_item_code(weapon)
        if code is None:
            continue

        weapons[str(weapon.GetUniqueID())] = {
            "code": code,
            "mark": weapon.Mark,
            "quantity": weapon.Quantity,
            "quick_slot": weapon.QuickSelectSlot,
        }

    return weapons


def collect_item_codes(
    pc: WillowPlayerController, inv_manager: WillowInventoryManager
) -> dict[str, InvItemSaveData]:
    items: dict[str, InvItemSaveData] = {}
    if inv_manager is None:
        return items  # pyright: ignore[reportUnreachable]

    _, item_list = inv_manager.GetItemList([], EPlayerDroppability.EPD_CannotDropOrSell, True)
    _, item_list = pc.FixAllItemsList(item_list)

    for item in item_list:
        if item is None:
            continue
        code = get_item_code(item)
        if code is None:
            continue
        items[str(item.GetUniqueID())] = {
            "code": code,
            "mark": item.Mark,
            "quantity": item.Quantity,
            "readied": item.bReadied,
        }

    return items


def collect_storage_codes(the_bank: WillowInventoryStorage) -> dict[str, ItemSaveData]:
    items: dict[str, ItemSaveData] = {}

    item_list = [data.Inventory for data in the_bank.TheChest if data.Inventory is not None]

    for item in item_list:
        if item is None:
            continue
        code = get_item_code(item)
        if code is None:
            continue
        items[str(item.GetUniqueID())] = {
            "code": code,
            "mark": item.Mark,
            "quantity": item.Quantity,
        }

    return items


def remove_backed_up_inv_codes(data: PlayerSaveData) -> None:
    for weapon_id in data["backup"]["weapons"]:
        if weapon_id in data["weapons"]:
            del data["weapons"][weapon_id]

    for item_id in data["backup"]["items"]:
        if item_id in data["items"]:
            del data["items"][item_id]


def remove_backed_up_bank_codes(data: PlayerSaveData) -> None:
    for item_id in data["backup"]["bank"]:
        if item_id in data["bank"]:
            del data["bank"][item_id]


def _restore_existing_entry[Record: ItemSaveData](
    current: DefinitionData,
    inventory_class: UClass,
    active: dict[str, Record],
    pending: dict[str, Record],
    next_backup: dict[str, Record],
    *,
    protect: bool,
) -> tuple[DefinitionData | None, Record | None]:
    global pending_missing_parts_warning
    item_id = str(current.UniqueId)

    source = active
    record = active.get(item_id)
    if record is None and protect:
        source = pending
        record = pending.get(item_id)
    if record is None:
        return None, None

    try:
        definition, missing = decode_modded_item_code(record["code"], inventory_class)
    except ItemCodeDecodeError as exc:
        logging.error(f"Could not decode inventory item {item_id}: {exc}")
        del source[item_id]
        return None, None

    if missing and protect:
        next_backup[item_id] = record
        pending_missing_parts_warning = True
        del source[item_id]
        return None, None

    definition.UniqueId = current.UniqueId
    del source[item_id]
    return definition, record


def _restore_unmatched_backups[Record: ItemSaveData](
    pending: dict[str, Record],
    active: dict[str, Record],
    append_entry: Callable[[DefinitionData, Record], None],
    protect: bool,
) -> None:
    global pending_missing_parts_warning
    for item_id, record in list(pending.items()):
        try:
            definition, missing = decode_modded_item_code(record["code"])
        except ItemCodeDecodeError as exc:
            logging.error(f"Could not decode inventory item {item_id}: {exc}")
            del pending[item_id]
            continue

        if missing:
            if not protect:
                del pending[item_id]
            else:
                pending_missing_parts_warning = True
            continue

        definition.UniqueId = int(item_id)
        append_entry(definition, record)
        active[item_id] = record
        del pending[item_id]


def restore_weapon_codes(save: PlayerSaveGame, save_data: PlayerSaveData) -> None:
    def append_weapon(definition: DefinitionData, record: WeaponSaveData) -> None:
        save.WeaponData.append(
            cast(
                "WeaponSaveGameData",
                unrealsdk.make_struct(
                    "WeaponSaveGameData",
                    WeaponDefinitionData=definition,
                    QuickSlot=record["quick_slot"],
                    Mark=record["mark"],
                ),
            )
        )

    new_backups: PlayerSaveItems = {
        "weapons": {},
        "items": save_data["backup"]["items"],
        "bank": save_data["backup"]["bank"],
    }
    new_weapons: dict[str, WeaponSaveData] = {}
    protect = PROTECT_ITEMS.value

    for entry in save.WeaponData:
        current = entry.WeaponDefinitionData
        primary = current.WeaponTypeDefinition
        weapon_class = (
            primary.InventoryClass if primary is not None else None
        ) or WILLOW_WEAPON_CLASS

        restored, record = _restore_existing_entry(
            current,
            weapon_class,
            save_data["weapons"],
            save_data["backup"]["weapons"],
            new_backups["weapons"],
            protect=protect,
        )
        if restored is not None:
            entry.WeaponDefinitionData = cast("WeaponDefinitionData", restored)
            if record is not None:
                new_weapons[str(entry.WeaponDefinitionData.UniqueId)] = record

    pending = save_data["weapons"].copy()
    if protect:
        pending = {**save_data["backup"]["weapons"], **pending}

    _restore_unmatched_backups(pending, new_weapons, append_weapon, protect)

    if protect:
        new_backups["weapons"] |= pending
    save_data["backup"] = new_backups
    save_data["weapons"] = new_weapons


def restore_item_codes(save: PlayerSaveGame, save_data: PlayerSaveData) -> None:
    def append_item(definition: DefinitionData, record: InvItemSaveData) -> None:
        save.ItemData.append(
            cast(
                "InventorySaveGameData",
                unrealsdk.make_struct(
                    "InventorySaveGameData",
                    DefinitionData=definition,
                    Quantity=record["quantity"],
                    bEquipped=record["readied"],
                    Mark=record["mark"],
                ),
            )
        )

    new_backups: PlayerSaveItems = {
        "weapons": save_data["backup"]["weapons"],
        "items": {},
        "bank": save_data["backup"]["bank"],
    }
    new_items: dict[str, InvItemSaveData] = {}

    protect = PROTECT_ITEMS.value

    for entry in save.ItemData:
        current = entry.DefinitionData
        primary = current.ItemDefinition
        item_class = (primary.InventoryClass if primary is not None else None) or WILLOW_ITEM_CLASS

        restored, record = _restore_existing_entry(
            current,
            item_class,
            save_data["items"],
            save_data["backup"]["items"],
            new_backups["items"],
            protect=protect,
        )
        if restored is not None:
            entry.DefinitionData = cast("ItemDefinitionData", restored)
            if record is not None:
                new_items[str(entry.DefinitionData.UniqueId)] = record

    pending = save_data["items"].copy()
    if protect:
        pending = {**save_data["backup"]["items"], **pending}

    _restore_unmatched_backups(pending, new_items, append_item, protect)

    if protect:
        new_backups["items"] |= pending
    save_data["backup"] = new_backups
    save_data["items"] = new_items


def restore_storage_codes(storage: WillowInventoryStorage, save_data: PlayerSaveData) -> None:
    global pending_missing_parts_warning
    active = save_data["bank"]
    pending = save_data["backup"]["bank"]
    new_bank: dict[str, ItemSaveData] = {}
    next_backup: dict[str, ItemSaveData] = {}
    protect = PROTECT_ITEMS.value
    pawn = storage.Outer.Owner
    live_ids: set[str] = set()

    for entry in storage.TheChest:
        item = entry.Inventory
        if item is None:
            continue

        is_weapon = item.Class._inherits(WILLOW_WEAPON_CLASS)
        if not is_weapon and not item.Class._inherits(WILLOW_ITEM_CLASS):
            continue

        item = cast("WillowWeapon | WillowItem", item)
        current = item.DefinitionData
        item_id = str(current.UniqueId)
        live_ids.add(item_id)

        restored, record = _restore_existing_entry(
            current, item.Class, active, pending, next_backup, protect=protect
        )
        if restored is None or record is None:
            continue

        mark = item.GetMark()
        quantity = item.Quantity
        item.InitializeFromDefinitionData(restored, pawn, False)  # pyright: ignore[reportArgumentType]
        item.Quantity = quantity
        item.SetMark(mark)
        new_bank[item_id] = record

    unmatched = {**pending, **active} if protect else active
    for item_id, record in unmatched.items():
        if item_id in live_ids:
            continue

        try:
            definition, missing = decode_modded_item_code(record["code"])
        except ItemCodeDecodeError as exc:
            logging.error(f"Could not decode inventory item {item_id}: {exc}")
            continue

        if missing:
            if protect:
                next_backup[item_id] = record
                pending_missing_parts_warning = True
            continue

        retry = next_backup if protect else new_bank
        if storage.GetSizeIncludingUnloadable() >= storage.GetMaxSize():
            retry[item_id] = record
            continue

        definition.UniqueId = int(item_id)
        if definition._type.Name == "WeaponDefinitionData":
            recovered = WILLOW_WEAPON_CLASS.ClassDefaultObject.CreateWeaponFromDef(
                definition, pawn, False
            )
            put = storage.PutWeapon
        else:
            recovered = WILLOW_ITEM_CLASS.ClassDefaultObject.CreateItemFromDef(
                definition, pawn, record["quantity"], False
            )
            put = storage.PutItem

        if recovered is None:
            retry[item_id] = record
            continue

        recovered.SetMark(record["mark"])
        if not put(recovered, False):
            recovered.Destroy()
            retry[item_id] = record
            continue

        new_bank[item_id] = record

    save_data["bank"] = new_bank
    save_data["backup"]["bank"] = next_backup
