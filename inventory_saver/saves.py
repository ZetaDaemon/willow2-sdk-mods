import json
from collections.abc import Callable
from pathlib import Path
from typing import TypedDict, TypeGuard

from mods_base import SETTINGS_DIR
from unrealsdk import logging

SAVES_DIR = SETTINGS_DIR / "inventory_saver"


class ItemSaveData(TypedDict):
    code: str
    mark: int
    quantity: int


class WeaponSaveData(ItemSaveData):
    quick_slot: int


class InvItemSaveData(ItemSaveData):
    readied: bool


class PlayerSaveItems(TypedDict):
    weapons: dict[str, WeaponSaveData]
    items: dict[str, InvItemSaveData]
    bank: dict[str, ItemSaveData]


class PlayerSaveData(PlayerSaveItems):
    backup: PlayerSaveItems


def _is_item_save_data(value: object) -> TypeGuard[ItemSaveData]:
    return (
        isinstance(value, dict)
        and isinstance(value.get("code"), str)
        and type(value.get("mark")) is int
        and type(value.get("quantity")) is int
    )


def _is_weapon_save_data(value: object) -> TypeGuard[WeaponSaveData]:
    return _is_item_save_data(value) and type(value.get("quick_slot")) is int


def _is_inv_item_save_data(value: object) -> TypeGuard[InvItemSaveData]:
    return _is_item_save_data(value) and type(value.get("readied")) is bool


def _is_save_map(value: object, is_record: Callable[[object], bool]) -> bool:
    return isinstance(value, dict) and all(
        isinstance(item_id, str) and is_record(record) for item_id, record in value.items()
    )


def _is_player_save_items(value: object) -> TypeGuard[PlayerSaveItems]:
    return (
        isinstance(value, dict)
        and _is_save_map(value.get("weapons"), _is_weapon_save_data)
        and _is_save_map(value.get("items"), _is_inv_item_save_data)
        and _is_save_map(value.get("bank"), _is_item_save_data)
    )


def is_player_save_data(value: object) -> TypeGuard[PlayerSaveData]:
    return _is_player_save_items(value) and _is_player_save_items(value.get("backup"))


def _new_save_items() -> PlayerSaveItems:
    return {"weapons": {}, "items": {}, "bank": {}}


def _new_save_data() -> PlayerSaveData:
    return {**_new_save_items(), "backup": _new_save_items()}


def get_save_path(save_id: int) -> Path:
    if save_id < 0:
        msg = "No character save ID assigned"
        raise ValueError(msg)

    SAVES_DIR.mkdir(parents=True, exist_ok=True)
    return SAVES_DIR / f"{save_id & 0xFFFF:04X}.json"


def load_player_save(save_id: int) -> PlayerSaveData:
    path = get_save_path(save_id)

    try:
        with path.open("r", encoding="utf-8") as file:
            data: object = json.load(file)
    except FileNotFoundError:
        return _new_save_data()
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        msg = f"Malformed inventory save at {path}"
        raise ValueError(msg) from exc

    if not is_player_save_data(data):
        msg = f"Invalid inventory save structure at {path}"
        raise ValueError(msg)

    return data


def save_player_save(save_id: int, data: PlayerSaveData) -> None:
    path = get_save_path(save_id)

    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)
